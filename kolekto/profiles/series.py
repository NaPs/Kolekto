from . import Profile


class TVSeries(Profile):

    """ A profile for tv series.
    """

    object_class = dict
    list_default_pattern = u'<b>{title}</b> ({year|"unknown"}) season <b>{season}</b> episode <b>{episode}</b>'
    list_default_order = ('title', 'year', 'season', 'episode')
