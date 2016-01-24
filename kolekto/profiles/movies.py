from . import Profile


class Movies(Profile):

    """ A profile for movies.
    """

    object_class = dict
    list_default_pattern = u'<b>{title}</b> ({year|"unknown"}) by {directors}'
    list_default_order = ('title', 'year')
