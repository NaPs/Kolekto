import json
import anydbm

from kubrick.movie import Movie

class MoviesMetadata(object):

    """ A database used to store metadata about movies managed by kubrick.
    """

    def __init__(self, filename):
        self._db = anydbm.open(filename, 'c')

    def get(self, movie_hash):
        """ Get information about a movie using its sha1.

        :param movie_hash: name of the movie
        """
        return Movie(json.loads(self._db[movie_hash]))

    def count(self):
        """ Count movies in the database.
        """
        return len(self._db)

    def save(self, movie_hash, movie):
        """ Save the specified movie on the database.

        :param movie_hash: the hash of the movie to save
        :param movie: the Movie object to save
        """
        self._db[movie_hash] = json.dumps(movie)
        self._db.sync()

    def remove(self, movie_hash):
        """ Remove the specified movie from the database.

        :param movie_hash: the hash of the movie to delete
        """
        del self._db[movie_hash]
        self._db.sync()

    def itermovieshash(self):
        """ Iterate over movies hash stored in the database.
        """
        return self._db.iterkeys()

    def itermovies(self):
        """ Iterate over (hash, movie) couple stored in database.
        """
        for movie_hash in self.itermovieshash():
            yield movie_hash, self.get(movie_hash)