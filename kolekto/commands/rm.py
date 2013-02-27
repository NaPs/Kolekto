import os

from kolekto.commands import Command
from kolekto.db import MoviesMetadata
from kolekto.printer import printer


class Rm(Command):

    """ Remove a movie from the kolekto tree.
    """

    help = 'remove a movie'

    def prepare(self):
        self.add_arg('movie_hash')

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))

        try:
            mdb.get(args.movie_hash)
        except KeyError:
            printer.p('Unknown movie hash.')
            return

        if printer.ask('Are you sure?', default=False):
            mdb.remove(args.movie_hash)
            printer.p('Removed. You need to launch gc to free space.')