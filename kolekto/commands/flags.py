import os

from kolekto.commands import Command
from kolekto.db import MoviesMetadata
from kolekto.printer import printer


class Watch(Command):

    """ Flag a movie as watched.
    """

    help = 'flag a movie as watched'

    def prepare(self):
        self.add_arg('movie_hash')
        self.add_arg('--unflag', '-u', action='store_true', default=False)

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))

        try:
            movie = mdb.get(args.movie_hash)
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
        mdb.save(args.movie_hash, movie)
