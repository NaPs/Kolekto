import re
import os
import json
from glob import glob
from hashlib import sha1
from tempfile import NamedTemporaryFile

from kolekto.printer import printer, bold
from kolekto.commands import Command
from kolekto.commands.show import show
from kolekto.datasources import MovieDatasource
from kolekto.movie import Movie
from kolekto.db import MoviesMetadata
from kolekto.exceptions import KolektoRuntimeError


def clean_title(title):
    match = re.match('(.+)((19|2\d)\d\d)', title)
    if match is None:
        return None, title
    else:
        title = match.group(1).replace('.', ' ').strip().title()
        year = int(match.group(2))
        return year, title


class Import(Command):

    """ Import movies into the Kolekto tree.
    """

    help = 'import a movie'

    def prepare(self):
        self.add_arg('file', nargs='+', help='Files to import (globbing allowed)')
        self.add_arg('--hardlink', action='store_true', default=False,
                     help='Create an hardlink instead of copying the file')
        self.add_arg('--symlink', action='store_true', default=False,
                     help='Create a symlink instead of copying the file')
        self.add_arg('--auto', '-a', action='store_true', default=False,
                     help='Automatically choose the most revelent movie.')
        self.add_arg('--dont-show', dest='show', action='store_false', default=True,
                     help='Show all informations about imported movie.')
        self.add_arg('--delete', action='store_true', default=False,
                     help='Delete imported file after a successful import')

    def run(self, args, config):
        # Check the args:
        if args.symlink and args.delete:
            raise KolektoRuntimeError('--delete can\'t be used with --symlink')
        elif args.symlink and args.hardlink:
            raise KolektoRuntimeError('--symlink and --hardlink are mutually exclusive')

        # Load the metadata database:
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))

        # Load informations from db:
        mds = MovieDatasource(config.subsections('datasource'), args.tree)

        for pattern in args.file:
            for filename in glob(pattern):
                filename = filename.decode('utf8')
                self._import(mdb, mds, args, config, filename)

    def _copy(self, tree, source_filename):
        """ Copy file in tree, show a progress bar during operations,
            and return the sha1 sum of copied file.
        """
        #_, ext = os.path.splitext(source_filename)
        filehash = sha1()
        with printer.progress(os.path.getsize(source_filename)) as update:
            with open(source_filename, 'rb') as fsource:
                with NamedTemporaryFile(dir=os.path.join(tree, '.kolekto', 'movies'), delete=False) as fdestination:
                    # Copy the source into the temporary destination:
                    while True:
                        buf = fsource.read(10 * 1024)
                        if not buf:
                            break
                        filehash.update(buf)
                        fdestination.write(buf)
                        update(len(buf))
                    # Rename the file to its final name or raise an error if
                    # the file already exists:
                    dest = os.path.join(tree, '.kolekto', 'movies', filehash.hexdigest())
                    if os.path.exists(dest):
                        raise IOError('This file already exists in tree (%s)' % filehash.hexdigest())
                    else:
                        os.rename(fdestination.name, dest)
        return filehash.hexdigest()

    def _link(self, tree, source_filename, symlink=False):
        filehash = sha1()
        with printer.progress(os.path.getsize(source_filename)) as update:
            with open(source_filename, 'rb') as fsource:
                    # Copy the source into the temporary destination:
                    while True:
                        buf = fsource.read(10 * 1024)
                        if not buf:
                            break
                        filehash.update(buf)
                        update(len(buf))
                    # Hardlink the file or raise an error if the file already exists:
                    dest = os.path.join(tree, '.kolekto', 'movies', filehash.hexdigest())
                    if os.path.exists(dest):
                        raise IOError('This file already exists in tree (%s)' % filehash.hexdigest())
                    else:
                        if symlink:
                            os.symlink(source_filename, dest)
                        else:
                            os.link(source_filename, dest)
        return filehash.hexdigest()

    def _import(self, mdb, mds, args, config, filename):
        printer.debug('Importing file {filename}', filename=filename)
        short_filename = os.path.basename(filename)
        title, ext = os.path.splitext(short_filename)

        year, title = clean_title(title)

        # Disable the year filter if auto mode is disabled:
        if not args.auto:
            year = None

        while True:
            # Disable the title input if auto mode is enabled:
            if not args.auto:
                title = printer.input(u'Title to search', default=title)
            datasource, movie = self._search(mds, title, short_filename, year, auto=args.auto)
            if datasource == 'manual':
                movie = Movie()
            elif datasource == 'abort':
                printer.p('Aborted import of {filename}', filename=filename)
                return
            break

        if datasource is None:
            return

        # Refresh the full data for the choosen movie:
        movie = mds.refresh(movie)

        if args.show:
            show(movie)
            printer.p('')

        # Edit available data:
        if not args.auto and printer.ask('Do you want to edit the movie metadata', default=False):
            movie = Movie(json.loads(printer.edit(json.dumps(movie, indent=True))))

        # Hardlink or copy the movie in the tree
        if args.hardlink or args.symlink:
            printer.p('\nComputing movie sha1sum...')
            movie_hash = self._link(args.tree, filename, args.symlink)
        else:
            printer.p('\nCopying movie in kolekto tree...')
            movie_hash = self._copy(args.tree, filename)
        printer.p('')

        mdb.save(movie_hash, movie)
        printer.debug('Movie {hash} saved to the database', hash=movie_hash)

        if args.delete:
            os.unlink(filename)
            printer.debug('Deleted original file {filename}', filename=filename)

    def _search(self, mdb, query, filename, year=None, auto=False):
        """ Search the movie using all available datasources and let the user
            select a result. Return the choosen datasource and produced movie dict.

        If auto is enabled, directly returns the first movie found.
        """
        choices = []
        for datasource, movie in mdb.search(query, year):
            if auto:
                return datasource, movie
            if movie.get('directors'):
                directors = ' by '
                if len(movie['directors']) > 1:
                    directors += '%s and %s' % (', '.join(movie['directors'][0:-1]),
                                                          movie['directors'][-1])
                else:
                    directors += movie['directors'][0]
            else:
                directors = ''
            fmt = u'{title} ({year}){directors} [{datasource}]'
            choices.append(((datasource, movie), fmt.format(title=bold(movie['title']),
                                                            year=movie.get('year', 'Unknown'),
                                                            directors=directors,
                                                            datasource=datasource.name)))

        if not choices:
            printer.p('No results to display for the file: {fn}', fn=filename)
            return None, None

        choices.append((('manual', None), 'Enter manually informations'))
        choices.append((('abort', None), 'None of these'))
        printer.p('Please choose the relevant movie for the file: {fn}', fn=filename, end='\n\n')
        return printer.choice(choices)
