""" Collection of helpers for Kolekto.
"""

import os


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
