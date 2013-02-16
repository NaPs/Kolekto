import os

from kubrick.commands import Command
from kubrick.db import MoviesMetadata
from kubrick.datasources import MovieDatasource
from kubrick.printer import printer

from fabulous.color import bold


def show(movie):
    """ Show the movie metadata.
    """
    for key, value in movie.iteritems():
        if isinstance(value, list):
            if not value:
                continue
            other = value[1:]
            value = value[0]
        else:
            other = []
        printer.p('{key}: {value}', key=bold(key), value=value)
        for value in other:
            printer.p('{pad}{value}', value=value, pad=' ' * (len(key) + 2))


class Show(Command):

    """ Show information about movies.
    """

    help = 'show informations about a movie'

    def prepare(self):
        self.add_arg('movie_hash')

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kub', 'metadata.db'))
        mds = MovieDatasource(config.subsections('datasource'), args.tree)

        try:
            movie = mdb.get(args.movie_hash)
        except KeyError:
            printer.p('Unknown movie hash.')
            return
        movie = mds.attach(args.movie_hash, movie)
        show(movie)