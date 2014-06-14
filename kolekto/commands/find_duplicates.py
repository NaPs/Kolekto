from collections import defaultdict

from kolekto.printer import printer
from kolekto.commands import Command
from kolekto.datasources import MovieDatasource


class FindDuplicates(Command):

    """ Find duplicate movies.
    """

    help = 'find duplicate movies in collection'

    def run(self, args, config):
        mds = MovieDatasource(config.subsections('datasource'), args.tree, self.profile.object_class)
        mdb = self.get_metadata_db(args.tree)
        hash_by_title = defaultdict(lambda: [])
        for movie_hash, movie in mdb.itermovies():
            movie = mds.attach(movie_hash, movie)
            hash_info = '<inv> %s </inv> (%s/%s)' % (movie_hash, movie.get('quality'), movie.get('ext'))
            hash_by_title[movie.get('title', None), movie.get('year', None)].append(hash_info)

        for (title, year), hashs in hash_by_title.iteritems():
            if len(hashs) > 1:
                printer.p('<b>{title}</b> ({year}): {hashs}', title=title,
                          year=year, hashs=' '.join(hashs))