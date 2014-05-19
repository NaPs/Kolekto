""" Movies database datasources.
"""

import pkg_resources

from confiture.schema.containers import Section, Value
from confiture.schema.types import String

from ..exceptions import KolektoRuntimeError


class DefaultDatasourceSchema(Section):

    _meta = {'args': Value(String()),
             'unique': True,
             'repeat': (0, None),
             'allow_unknown': True}


class Datasource(object):

    """ Base class for all movies database datasources.
    """

    config_schema = DefaultDatasourceSchema()

    def __init__(self, name, tree, config, object_class=dict):
        self.name = name
        self.tree = tree
        self.config = config
        self.object_class = object_class

    def search(self, title, year=None):
        """ Search for a movie title in database.

        :return: a list of Movie object
        """
        return []

    def refresh(self, movie):
        """ Refresh the movie's metadata.
        """

    def attach(self, movie_hash, movie):
        return movie


class MovieDatasource(object):

    """ Movie database.
    """

    def __init__(self, datasources_config, tree, object_class=dict):
        self._object_class = object_class
        self._datasources = []
        for datasource_config in datasources_config:
            entrypoints = tuple(pkg_resources.iter_entry_points('kolekto.datasources', datasource_config.args))
            if not entrypoints:
                raise KolektoRuntimeError('Bad datasource %r' % datasource_config.args)
            datasource_class = entrypoints[0].load()
            datasource_config = datasource_class.config_schema.validate(datasource_config)
            ds = datasource_class(entrypoints[0].name, tree, datasource_config, self._object_class)
            self._datasources.append(ds)

    def search(self, title, **kwargs):
        for datasource in self._datasources:
            for movie in datasource.search(title, **kwargs):
                yield datasource, movie

    def refresh(self, movie):
        for datasource in self._datasources:
            refreshed = datasource.refresh(movie)
            if refreshed:
                movie.update(refreshed)
        return movie

    def attach(self, movie_hash, movie):
        for datasource in self._datasources:
            movie = datasource.attach(movie_hash, movie)
        return movie