import os

from kolekto.printer import printer
from kolekto.commands import Command
from kolekto.db import MoviesMetadata
from kolekto.datasources import MovieDatasource
from kolekto.commands.show import show


class Refresh(Command):

    """ Refresh metadata of movies.
    """

    help = 'refresh metadata of movies'

    def prepare(self):
        self.add_arg('movie_hash', nargs='?',
                     help='Hash of the movie to refresh. If not specified, '
                          'refresh all movies.')

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))
        mds = MovieDatasource(config.subsections('datasource'), args.tree)

        if args.movie_hash is None: # Refresh all movies
            if printer.ask('Would you like to refresh all movies?', default=True):
                with printer.progress(mdb.count(), task=True) as update:
                    for movie_hash, movie in list(mdb.itermovies()):
                        movie = mds.refresh(movie)
                        mdb.save(movie_hash, movie)
                        printer.verbose('Saved {hash}', hash=movie_hash)
                        update(1)
        else:
            try:
                movie = mdb.get(args.movie_hash)
            except KeyError:
                printer.p('Unknown movie hash.')
                return
            else:
                movie = mds.refresh(movie)
                show(movie)
                if printer.ask('Would you like to save the movie?', default=True):
                    mdb.save(args.movie_hash, movie)
                    printer.p('Saved.')

