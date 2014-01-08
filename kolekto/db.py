from kolekto.helpers import JsonDbm


class MoviesMetadata(JsonDbm):

    """ A database used to store metadata about movies managed by kolekto.
    """

    def itermovieshash(self):
        """ Iterate over movies hash stored in the database.
        """
        cur = self._db.firstkey()
        while cur is not None:
            yield cur
            cur = self._db.nextkey(cur)

    def itermovies(self):
        """ Iterate over (hash, movie) couple stored in database.
        """
        return self.iteritems()