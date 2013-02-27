import os
from collections import defaultdict

from kolekto.printer import printer, bold
from kolekto.commands import Command
from kolekto.db import MoviesMetadata


class FindDuplicates(Command):

    """ Find duplicate movies.
    """

    help = 'find duplicate movies in collection'

    def run(self, args, config):
        mdb = MoviesMetadata(os.path.join(args.tree, '.kolekto', 'metadata.db'))
        hash_by_title = defaultdict(lambda: [])
        for movie_hash, movie in mdb.itermovies():
            hash_by_title[movie.get('title', None), movie.get('year', None)].append(movie_hash)

        for (title, year), hashs in hash_by_title.iteritems():
            if len(hashs) > 1:
                printer.p('{title} ({year}): {hashs}', title=bold(title),
                          year=year, hashs=' '.join(hashs))