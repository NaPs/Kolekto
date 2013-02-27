import os

from kolekto.commands import Command
from kolekto.db import MoviesMetadata
from kolekto.printer import printer, bold, highlight_white


class List(Command):

    """ List movies in the kolekto tree.
    """

    help = 'list movies'

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))
        movies = sorted(mdb.itermovies(), key=lambda x: (x[1].get('title'), x[1].get('year')))
        for movie_hash, movie in movies:
            if movie.get('directors'):
                directors = ' by '
                if len(movie['directors']) > 1:
                    directors += '%s and %s' % (', '.join(movie['directors'][0:-1]),
                                                          movie['directors'][-1])
                else:
                    directors += movie['directors'][0]
            else:
                directors = ''
            fmt = u'{hash} {title} ({year}){directors}'
            printer.p(fmt, title=bold(movie.get('title', 'No title')),
                           year=movie.get('year', 'Unknown'),
                           directors=directors,
                           hash=highlight_white(' ' + movie_hash + ' '))
