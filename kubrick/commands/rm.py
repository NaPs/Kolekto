import os

from kubrick.commands import Command
from kubrick.db import MoviesMetadata
from kubrick.printer import printer


class Rm(Command):

    """ Remove a movie from the kubrick tree.
    """

    help = 'remove a movie'

    def prepare(self):
        self.add_arg('movie_hash')

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kub', 'metadata.db'))

        try:
            mdb.get(args.movie_hash)
        except KeyError:
            printer.p('Unknown movie hash.')
            return

        if printer.ask('Are you sure?', default=False):
            mdb.remove(args.movie_hash)
            printer.p('Removed. You need to launch gc to free space.')