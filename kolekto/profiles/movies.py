import unicodedata
import re

from . import Profile


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

    def __unicode__(self):
        if self.get('directors'):
            directors = ' by '
            if len(self['directors']) > 1:
                directors += '%s and %s' % (', '.join(self['directors'][0:-1]),
                                                      self['directors'][-1])
            else:
                directors += self['directors'][0]
        else:
            directors = ''
        fmt = u'<b>{title}</b> ({year}){directors}'
        return fmt.format(title=self.get('title', 'No title'),
                          year=self.get('year', 'Unknown'),
                          directors=directors)


class Movies(Profile):

    """ A profile for movies.
    """

    object_class = Movie
