class Command(object):

    """
    Base class for all commands.

    :cvar help: the help for the command
    """

    help = ''

    def __init__(self, name, aparser_subs):
        self._aparser = aparser_subs.add_parser(name, help=self.help)
        self._aparser.set_defaults(command=self.run, command_name=name)

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
