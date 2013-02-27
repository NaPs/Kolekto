import os
import json

from kolekto.printer import printer
from kolekto.commands import Command
from kolekto.db import MoviesMetadata


class Dump(Command):

    """ Dump the whole database into json.
    """

    help = 'dump database into json'

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))
        dump = [{'hash': x, 'movie': y} for x, y in mdb.itermovies()]
        json.dump(dump, printer.output)