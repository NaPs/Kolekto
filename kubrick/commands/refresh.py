import os

from kubrick.printer import printer
from kubrick.commands import Command
from kubrick.db import MoviesMetadata
from kubrick.datasources import MovieDatasource
from kubrick.commands.show import show


class Refresh(Command):

    """ Refresh metadata of movies.
    """

    help = 'refresh metadata of movies'

    def prepare(self):
        self.add_arg('movie_hash', nargs='?')

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kub', 'metadata.db'))
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

