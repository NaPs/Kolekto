import os

from kubrick.printer import printer
from kubrick.commands import Command
from kubrick.exceptions import KubrickRuntimeError
from kubrick.db import MoviesMetadata


DEFAULT_CONFIG = '''
view 'Titles' {
    pattern = '{title}.{ext}'
}

# By default, the tree will use the tmdb_proxy datasource which will allow
# you to get data from TMDB without requiring an API key:
datasource 'tmdb_proxy' {
    base_url = 'http://api.kubrick-project.org/'
    max_results = 2
}

# Uncomment and enter your API key to enable the TMDB datasource:
#datasource 'tmdb' {
#    api_key = '<enter your tmdb api key>'
#    max_results = 2
#}

# Get informations from files (quality, runtime...):
datasource 'mediainfos' {}
'''


class Init(Command):

    """ Create links in the kubrick tree.
    """

    help = 'initialize a new Kubrick tree'

    def run(self, args, config):
        if config is not None:
            raise KubrickRuntimeError('Already a Kubrick tree')

        movies_directory = os.path.join(args.tree, '.kub', 'movies')

        # Ensure that the .kub/movies directory exists:
        if not os.path.isdir(movies_directory):
            os.makedirs(movies_directory)

        # Write the default config:
        with open(os.path.join(args.tree, '.kub', 'config'), 'w') as fconfig:
            fconfig.write(DEFAULT_CONFIG)
        printer.p('Initialized empty Kubrick tree in {where}.', where=args.tree)

        # Open the metadata db to create it automatically:
        MoviesMetadata(os.path.join(args.tree, '.kub', 'metadata.db'))
