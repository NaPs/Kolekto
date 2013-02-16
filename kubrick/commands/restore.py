import os
import json

from kubrick.printer import printer
from kubrick.commands import Command
from kubrick.db import MoviesMetadata


class Restore(Command):

    """ Restore metadata from a json dump.
    """

    help = 'Restore metadata from a json dump'

    def prepare(self):
        self.add_arg('file', help='The json dump file to restore')

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kub', 'metadata.db'))
        with open(args.file) as fdump:
            dump = json.load(fdump)
        for movie in dump:
            mdb.save(movie['hash'], movie['movie'])
            printer.verbose('Loaded {hash}', hash=movie['hash'])
        printer.p('Loaded {nb} movies.', nb=len(dump))
