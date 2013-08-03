import os

from kolekto.db import MoviesMetadata


class Command(object):

    """
    Base class for all commands.

    :cvar help: the help for the command
    """

    help = ''

    def __init__(self, name, profile, aparser_subs):
        self._aparser = aparser_subs.add_parser(name, help=self.help)
        self._profile = profile
        self._aparser.set_defaults(command=self.run, command_name=name)

    @property
    def profile(self):
        return self._profile

    def add_arg(self, *args, **kwargs):
        """ Add an argument to the command argument parser.
        """

        self._aparser.add_argument(*args, **kwargs)

    def prepare(self):
        """ Method to override, executed before to parse arguments from command
            line. This is a good place to call :meth:`add_arg`.
        """
        pass

    def run(self, args, config):
        """ Method to override, executed if command has been selected.

        :param args: parsed arguments
        :param config: parsed configuration
        """
        pass

    def get_metadata_db(self, tree):
        return MoviesMetadata(os.path.join(tree, '.kolekto', 'metadata.db'),
                              object_class=self.profile.object_class)