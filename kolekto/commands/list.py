from kolekto.commands import Command
from kolekto.printer import printer, bold, highlight_white


class List(Command):

    """ List movies in the kolekto tree.
    """

    help = 'list movies'

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)
        movies = sorted(mdb.itermovies(), key=lambda x: (x[1].get('title'), x[1].get('year')))
        for movie_hash, movie in movies:
            printer.p(u'{hash} {movie}',
                      hash=highlight_white(' ' + movie_hash + ' '),
                      movie=unicode(movie))
