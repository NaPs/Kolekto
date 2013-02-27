import os

from kolekto.printer import printer
from kolekto.commands import Command
from kolekto.exceptions import KolektoRuntimeError
from kolekto.db import MoviesMetadata


DEFAULT_CONFIG = '''
view 'Titles' {
    pattern = '{title}.{ext}'
}

# By default, the tree will use the tmdb_proxy datasource which will allow
# you to get data from TMDB without requiring an API key:
datasource 'tmdb_proxy' {
    base_url = 'http://api.kolekto-project.org/'
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

    """ Create links in the kolekto tree.
    """

    help = 'initialize a new Kolekto tree'

    def run(self, args, config):
        if config is not None:
            raise KolektoRuntimeError('Already a Kolekto tree')

        movies_directory = os.path.join(args.tree, '.kolekto', 'movies')

        # Ensure that the .kolekto/movies directory exists:
        if not os.path.isdir(movies_directory):
            os.makedirs(movies_directory)

        # Write the default config:
        with open(os.path.join(args.tree, '.kolekto', 'config'), 'w') as fconfig:
            fconfig.write(DEFAULT_CONFIG)
        printer.p('Initialized empty Kolekto tree in {where}.', where=os.path.abspath(args.tree))

        # Open the metadata db to create it automatically:
        MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))
