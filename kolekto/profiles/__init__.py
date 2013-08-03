from itertools import chain

import pkg_resources


class Profile(object):

    object_class = dict

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def _get_entrypoints(self):
        return chain(pkg_resources.iter_entry_points(group='kolekto.commands.%s' % self.name),
                     pkg_resources.iter_entry_points(group='kolekto.commands'),
                     pkg_resources.iter_entry_points(group='kolekto.commands.no_profile'))

    def load_commands(self, parser):
        """ Load commands of this profile.

        :param parser: argparse parser on which to add commands
        """

        entrypoints = self._get_entrypoints()

        already_loaded = set()
        for entrypoint in entrypoints:
            if entrypoint.name not in already_loaded:
                command_class = entrypoint.load()
                command_class(entrypoint.name, self, parser).prepare()
                already_loaded.add(entrypoint.name)


class NoProfileProfile(Profile):

    """ Special profile used when no profile is loaded.
    """

    def _get_entrypoints(self):
        return pkg_resources.iter_entry_points(group='kolekto.commands.no_profile')
