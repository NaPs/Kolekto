import unicodedata
import re

from . import Profile
from ..printer import bold


class Movie(dict):

    """ Represent a movie in a dict.
    """

    @property
    def slug(self):
        """ Get a slug from the movie title.
        """
        slug = unicodedata.normalize('NFKD', self['title']).encode('ascii', 'ignore')
        slug = slug.lower().replace(' ', '_')
        slug = re.sub(r'[^a-z0-9_]', '', slug)
        return slug


class Movies(Profile):

    """ A profile for movies.
    """

    object_class = Movie
