""" Collection of helpers for Kolekto.
"""

import os
import gdbm
import json

def get_hash(input_string):
    """ Return the hash of the movie depending on the input string.

    If the input string looks like a symbolic link to a movie in a Kolekto
    tree, return its movies hash, else, return the input directly in lowercase.
    """

    # Check if the input looks like a link to a movie:
    if os.path.islink(input_string):
        directory, movie_hash = os.path.split(os.readlink(input_string))
        input_string = movie_hash

    return input_string.lower()


class JsonDbm(object):

    """ A simple GNU DBM database which store JSON-serialized Python.
    """

    def __init__(self, filename, object_class=dict):
        self._db = gdbm.open(filename, 'c')
        self._object_class = object_class

    def __contains__(self, key):
        return key in self._db

    def get(self, key):
        """ Get data associated with provided key.
        """
        return self._object_class(json.loads(self._db[key]))

    def count(self):
        """ Count records in the database.
        """
        return len(self._db)

    def save(self, key, data):
        """ Save data associated with key.
        """
        self._db[key] = json.dumps(data)
        self._db.sync()

    def remove(self, key):
        """ Remove the specified key from the database.
        """
        del self._db[key]
        self._db.sync()

    def iteritems(self):
        """ Iterate over (key, data) couple stored in database.
        """
        for key in self.itermovieshash():
            yield key, self.get(key)