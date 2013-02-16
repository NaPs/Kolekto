import os

from kubrick.printer import printer
from kubrick.commands import Command


class Config(Command):

    """ Edit the configuration file.
    """

    help = 'edit the configuration file'

    def run(self, args, config):
        config_fullname = os.path.join(args.tree, '.kub', 'config')
        with open(config_fullname, 'r+') as fconfig:
            config = printer.edit(fconfig.read())
            fconfig.seek(0)
            fconfig.truncate()
            fconfig.write(config)
        printer.p('Saved.')