import os
from itertools import product, izip

from kolekto.printer import printer
from kolekto.commands import Command
from kolekto.datasources import MovieDatasource
from kolekto.pattern import parse_pattern


class FormatWrapper(object):

    """ A wrapper used to customize how movies attributes are formatted.
    """

    def __init__(self, title, obj):
        self.title = title
        self.obj = obj

    def __unicode__(self):
        if isinstance(self.obj, bool):
            if self.obj:
                return self.title.title()
        return unicode(self.obj)


def format_all(format_string, env):
    """ Format the input string using each possible combination of lists
        in the provided environment. Returns a list of formated strings.
    """

    prepared_env = parse_pattern(format_string, env, lambda x, y: [FormatWrapper(x, z) for z in y])
    # Generate each possible combination, format the string with it and yield
    # the resulting string:
    for field_values in product(*prepared_env.itervalues()):
        format_env = dict(izip(prepared_env.iterkeys(), field_values))
        yield format_string.format(**format_env)


def walk_links(directory, prefix='', linkbase=None):
    """ Return all links contained in directory (or any sub directory).
    """
    links = {}
    try:
        for child in os.listdir(directory):
            fullname = os.path.join(directory, child)
            if os.path.islink(fullname):
                link_path = os.path.normpath(os.path.join(directory, os.readlink(fullname)))
                if linkbase:
                    link_path = os.path.relpath(link_path, linkbase)
                links[os.path.join(prefix, child)] = link_path
            elif os.path.isdir(fullname):
                links.update(walk_links(fullname,
                                        prefix=os.path.join(prefix, child),
                                        linkbase=linkbase))
    except OSError as err:
        if err.errno != 2:  # Ignore unknown directory error
            raise
    return links


class Link(Command):

    """ Create links in the kolekto tree.
    """

    help = 'create symlinks'

    def prepare(self):
        self.add_arg('--dry-run', '-d', action='store_true', default=False,
                     help='Do not create or delete any link')

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)
        mds = MovieDatasource(config.subsections('datasource'), args.tree, self.profile.object_class)

        if args.dry_run:
            printer.p('Dry run: I will not create or delete any link')

        # Create the list of links that must exists on the fs:
        db_links = {}
        with printer.progress(mdb.count(), task=True) as update:
            for movie_hash, movie in mdb.itermovies():
                movie = mds.attach(movie_hash, movie)
                for view in config.subsections('view'):
                    for pattern in view.get('pattern'):
                        for result in format_all(pattern, movie):
                            filename = os.path.join(view.args, result)
                            if filename in db_links:
                                printer.p('Warning: duplicate link {link}', link=filename)
                            else:
                                db_links[filename] = movie_hash
                update(1)

        # Create the list of links already existing on the fs:
        fs_links = {}
        for view in config.subsections('view'):
            view_links = walk_links(os.path.join(args.tree, view.args),
                                    prefix=view.args,
                                    linkbase=os.path.join(args.tree, '.kolekto', 'movies'))
            fs_links.update(view_links)

        db_links = set(db_links.iteritems())
        fs_links = set(fs_links.iteritems())

        links_to_delete = fs_links - db_links
        links_to_create = db_links - fs_links

        printer.p('Found {rem} links to delete, {add} links to create',
                  rem=len(links_to_delete),
                  add=len(links_to_create))

        dirs_to_cleanup = set()

        # Delete the old links:
        for filename, link in links_to_delete:
            printer.verbose('Deleting {file}', file=filename)
            if not args.dry_run:
                os.remove(os.path.join(args.tree, filename))
            while filename:
                filename = os.path.split(filename)[0]
                dirs_to_cleanup.add(filename)

        dirs_to_cleanup.discard('')  # Avoid to delete view roots

        # Delete empty directories:
        for directory in dirs_to_cleanup:
            if not args.dry_run:
                try:
                    os.rmdir(os.path.join(args.tree, directory))
                except OSError, err:
                    if err.errno != 39:  # Ignore "Directory not empty" error
                        raise
                else:
                    printer.verbose('Deleted directory {dir}', dir=directory)

        # Create the new links:
        for filename, link in links_to_create:
            fullname = os.path.join(args.tree, filename)
            dirname = os.path.dirname(fullname)
            movie_link = os.path.join(args.tree, '.kolekto', 'movies', link)
            printer.verbose('Link: {file!r} -> {link!r}', file=filename, link=link)
            if not args.dry_run:
                try:
                    os.makedirs(dirname)
                except OSError as err:
                    if err.errno != 17:  # Ignore already existing directory error
                        raise
                os.symlink(os.path.relpath(movie_link, dirname), fullname)