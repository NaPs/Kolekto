import os

from kolekto.commands import Command
from kolekto.db import MoviesMetadata
from kolekto.printer import printer
from kolekto.helpers import get_hash


class Watch(Command):

    """ Flag a movie as watched.
    """

    help = 'flag a movie as watched'

    def prepare(self):
        self.add_arg('input', metavar='movie-hash-or-file')
        self.add_arg('--unflag', '-u', action='store_true', default=False)

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))

        movie_hash = get_hash(args.input)

        try:
            movie = mdb.get(movie_hash)
        except KeyError:
            printer.p('Unknown movie hash.')
            return
        if args.unflag:
            try:
                del movie['watched']
            except KeyError:
                pass
        else:
            movie['watched'] = True
        mdb.save(movie_hash, movie)
