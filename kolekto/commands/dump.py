import json

from kolekto.printer import printer
from kolekto.commands import Command


class Dump(Command):

    """ Dump the whole database into json.
    """

    help = 'dump database into json'

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)
        dump = [{'hash': x, 'movie': y} for x, y in mdb.itermovies()]
        json.dump(dump, printer.output)