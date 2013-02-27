import os

from kolekto.printer import printer
from kolekto.commands import Command


class Config(Command):

    """ Edit the configuration file.
    """

    help = 'edit the configuration file'

    def run(self, args, config):
        config_fullname = os.path.join(args.tree, '.kolekto', 'config')
        with open(config_fullname, 'r+') as fconfig:
            config = printer.edit(fconfig.read())
            fconfig.seek(0)
            fconfig.truncate()
            fconfig.write(config)
        printer.p('Saved.')