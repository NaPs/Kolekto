import os
import json
from glob import glob
from hashlib import sha1
from tempfile import NamedTemporaryFile

from kubrick.printer import printer, bold
from kubrick.commands import Command
from kubrick.datasources import MovieDatasource
from kubrick.movie import Movie
from kubrick.db import MoviesMetadata


class Import(Command):

    """ Import movies into the Kubrick tree.
    """

    help = 'import a movie'

    def prepare(self):
        self.add_arg('file', nargs='+', help='Files to import (globbing allowed)')
        self.add_arg('--hardlink', action='store_true', default=False,
                     help='Create an hardlink instead of copying the file')

    def run(self, args, config):
        # Load the metadata database:
        mdb = MoviesMetadata(os.path.join(args.tree, '.kub', 'metadata.db'))

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
                with NamedTemporaryFile(dir=os.path.join(tree, '.kub', 'movies'), delete=False) as fdestination:
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
                    dest = os.path.join(tree, '.kub', 'movies', filehash.hexdigest())
                    if os.path.exists(dest):
                        raise IOError('This file already exists in tree (%s)' % filehash.hexdigest())
                    else:
                        os.rename(fdestination.name, dest)
        return filehash.hexdigest()

    def _hardlink(self, tree, source_filename):
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
                    dest = os.path.join(tree, '.kub', 'movies', filehash.hexdigest())
                    if os.path.exists(dest):
                        raise IOError('This file already exists in tree (%s)' % filehash.hexdigest())
                    else:
                        os.link(source_filename, dest)
        return filehash.hexdigest()

    def _import(self, mdb, mds, args, config, filename):
        printer.debug('Importing file {filename}', filename=filename)
        short_filename = os.path.basename(filename)
        title, ext = os.path.splitext(short_filename)

        while True:
            title = printer.input(u'Title to search', default=title)
            datasource, movie = self._search(mds, title, short_filename)
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

        # Edit available data:
        if printer.ask('Do you want to edit the movie metadata', default=False):
            movie = Movie(json.loads(printer.edit(json.dumps(movie, indent=True))))

        # Hardlink or copy the movie in the tree
        if args.hardlink:
            printer.p('\nComputing movie sha1sum...')
            movie_hash = self._hardlink(args.tree, filename)
        else:
            printer.p('\nCopying movie in kubrick tree...')
            movie_hash = self._copy(args.tree, filename)
        printer.p('')

        mdb.save(movie_hash, movie)
        printer.debug('Movie {hash} saved to the database', hash=movie_hash)

    def _search(self, mdb, query, filename):
        """ Search the movie using all available datasources and let the user
            select a result. Return the choosen datasource and produced movie dict.
        """
        choices = []
        for datasource, movie in mdb.search(query):
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
