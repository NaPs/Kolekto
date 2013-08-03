from kolekto.commands import Command
from kolekto.printer import printer
from kolekto.helpers import get_hash


class Rm(Command):

    """ Remove a movie from the kolekto tree.
    """

    help = 'remove a movie'

    def prepare(self):
        self.add_arg('input', metavar='movie-hash-or-file')

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)

        movie_hash = get_hash(args.input)

        try:
            mdb.get(movie_hash)
        except KeyError:
            printer.p('Unknown movie hash.')
            return

        if printer.ask('Are you sure?', default=False):
            mdb.remove(movie_hash)
            printer.p('Removed. You need to launch gc to free space.')