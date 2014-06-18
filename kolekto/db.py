import os
import shutil

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


class AttachmentStore(object):

    """ An abstraction layer to the attachments stored in the tree.
    """

    def __init__(self, directory):
        self.directory = directory

    def store(self, movie_hash, name, file):
        movie_directory = os.path.join(self.directory, movie_hash)
        try:
            os.makedirs(movie_directory)
        except OSError as err:
            if err.errno != 17:  # Ignore already existing directories
                raise
        attachment_fullname = os.path.join(movie_directory, name)
        with open(attachment_fullname, 'w') as fattach:
            shutil.copyfileobj(file, fattach)

    def list(self, movie_hash):
        movie_directory = os.path.join(self.directory, movie_hash)
        try:
            return os.listdir(movie_directory)
        except OSError as err:
            if err.errno == 2:
                return []
            else:
                raise

    def exists(self, movie_hash, name):
        attachment_fullname = os.path.join(self.directory, movie_hash, name)
        return os.path.isfile(attachment_fullname)
