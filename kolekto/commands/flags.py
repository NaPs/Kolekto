from kolekto.commands import Command
from kolekto.printer import printer
from kolekto.helpers import get_hash


class FlagCommand(Command):

    flags = []  # Flags to set when this flag is set
    unset_flags = []  # Flags to unset when this flag is set
    unflag_unset_flags = []  # Flags to unset when this flag is unset

    def prepare(self):
        self.add_arg('input', metavar='movie-hash-or-file')
        self.add_arg('--unflag', '-u', action='store_true', default=False)

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)

        movie_hash = get_hash(args.input)

        try:
            movie = mdb.get(movie_hash)
        except KeyError:
            printer.p('Unknown movie hash.')
            return
        if args.unflag:
            for flag in self.unflag_unset_flags:
                try:
                    del movie[flag]
                except KeyError:
                    pass
        else:
            for flag in self.flags:
                movie[flag] = True
            for flag in self.unset_flags:
                try:
                    del movie[flag]
                except KeyError:
                    pass
        mdb.save(movie_hash, movie)


class Watch(FlagCommand):

    """ Flag a movie as watched.
    """

    flags = ['watched']
    unflag_unset_flags = ['watched', 'favorite', 'crap']
    help = 'flag a movie as watched'


class Favorite(FlagCommand):

    """ Flag a movie as favorite.
    """

    flags = ['favorite', 'watched']
    unset_flags = ['crap']
    unflag_unset_flags = ['favorite']
    help = 'flag a movie as favorite (and also set it as watched)'


class Crap(FlagCommand):

    """ Flag a movie as crap.
    """

    flags = ['crap', 'watched']
    unset_flags = ['favorite']
    unflag_unset_flags = ['crap']
    help = 'flag a movie as crap (and also set it as watched)'
