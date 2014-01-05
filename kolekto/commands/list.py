from kolekto.commands import Command
from kolekto.printer import printer
from kolekto.exceptions import KolektoRuntimeError
from kolekto.pattern import parse_pattern


DEFAULT_PATTERN = u'<b>{title}</b> ({year|"unknown"}) by {directors}'


class ListingFormatWrapper(object):

    """ A wrapper used to customize how movies attributes are formatted.
    """

    def __init__(self, title, obj):
        self.title = title
        self.obj = obj

    def __unicode__(self):
        if isinstance(self.obj, bool):
            if self.obj:
                return self.title.title()
        elif isinstance(self.obj, list):
            if not self.obj:
                return 'None'  # List is empty
            elif len(self.obj) > 1:
                return '%s and %s' % (', '.join(self.obj[0:-1]), self.obj[-1])
            else:
                return unicode(self.obj[0])
        else:
            return unicode(self.obj)

    def __repr__(self):
        return repr(self.obj)


class List(Command):

    """ List movies in the kolekto tree.
    """

    help = 'list movies'

    def prepare(self):
        self.add_arg('listing', metavar='listing', default='default', nargs='?')

    def _config(self, args, config):
        """ Get configuration for the current used listing.
        """
        listings = dict((x.args, x) for x in config.subsections('listing'))
        listing = listings.get(args.listing)
        if listing is None:
            if args.listing == u'default':
                return {'pattern': DEFAULT_PATTERN}
            else:
                raise KolektoRuntimeError('Unknown listing %r' % args.listing)
        else:
            return {'pattern': listing.get('pattern')}

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)
        listing = self._config(args, config)
        movies = sorted(mdb.itermovies(), key=lambda x: (x[1].get('title'), x[1].get('year')))
        # Get the current used listing:
        for movie_hash, movie in movies:
            prepared_env = parse_pattern(listing['pattern'], movie, ListingFormatWrapper)
            printer.p(u'<inv><b> {hash} </b></inv> ' + listing['pattern'], hash=movie_hash, **prepared_env)