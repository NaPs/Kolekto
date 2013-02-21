""" The moviedb database for Kubrick.
"""

import json
import requests
import time
from datetime import datetime

from kubrick.printer import printer
from kubrick.datasources import Datasource, DefaultDatasourceSchema
from kubrick.movie import Movie
from kubrick.exceptions import KubrickRuntimeError

from dotconf.schema.containers import Value
from dotconf.schema.types import String, Integer


class TmdbDatasourceSchema(DefaultDatasourceSchema):

    api_key = Value(String())
    max_results = Value(Integer(min=1), default=None)


class TmdbDatasource(Datasource):

    config_schema = TmdbDatasourceSchema()

    URL_SEARCH = (u'http://api.themoviedb.org/3/search/movie'
                   '?api_key=%(api_key)s&query=%(query)s')
    URL_GET = u'http://api.themoviedb.org/3/movie/%(id)s?api_key=%(api_key)s'
    URL_CAST = u'http://api.themoviedb.org/3/movie/%(id)s/casts?api_key=%(api_key)s'
    URL_ALT = u'http://api.themoviedb.org/3/movie/%(id)s/alternative_titles?api_key=%(api_key)s'

    def _tmdb_search(self, title):
        ak = self.config.get('api_key')
        url = self.URL_SEARCH % dict(api_key=ak, query=requests.utils.quote(title.encode('utf8')))
        response = requests.get(url.encode('utf8'))
        return json.loads(response.text)

    def _get(self, url, *args, **kwargs):
        ak = self.config.get('api_key')
        url = url % dict(api_key=ak, **kwargs)
        for _ in xrange(3):
            printer.debug('Requesting {url}', url=url)
            response = requests.get(url)
            if not 200 <= response.status_code < 400 :
                printer.debug('Got error ({http_err}), retrying in 3s...', http_err=response.status_code)
                time.sleep(3)
                continue
            return json.loads(response.text)
        else:
            raise KubrickRuntimeError('Unable to get the URL')

    def _tmdb_get(self, movie_id):
        return self._get(self.URL_GET, id=movie_id)

    def _tmdb_cast(self, movie_id):
        return self._get(self.URL_CAST, id=movie_id)

    def _tmdb_alt(self, movie_id):
        return self._get(self.URL_ALT, id=movie_id)

    def search(self, title):
        results = self._tmdb_search(title)['results']
        if self.config.get('max_results') is not None:
            results = results[:self.config.get('max_results')]
        for result in results:
            details = self._tmdb_get(result['id'])
            cast = self._tmdb_cast(result['id'])
            movie = Movie({'title': result['original_title'],
                           'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing'],
                           '_datasource': self.name,
                           '_tmdb_id': result['id']})
            if details.get('release_date'):
                movie['year'] = datetime.strptime(details['release_date'], '%Y-%m-%d').year
            yield movie

    def refresh(self, movie):
        """ Try to refresh metadata of the movie through the datasource.
        """
        if '_tmdb_id' in movie:
            tmdb_id = movie['_tmdb_id']
            details = self._tmdb_get(tmdb_id)
            cast = self._tmdb_cast(tmdb_id)
            alternatives = self._tmdb_alt(tmdb_id)
            refreshed = Movie({'title': details['original_title'],
                               'score': details['popularity'],
                               'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing'],
                               'writers': [x['name'] for x in cast['crew'] if x['department'] == 'Writing'],
                               'cast': [x['name'] for x in cast['cast']],
                               'genres': [x['name'] for x in details['genres']],
                               'countries': [x['name'] for x in details['production_countries']],
                               '_Datasource': self.name,
                               '_tmdb_id': tmdb_id})
            if details.get('release_date'):
                refreshed['year'] = datetime.strptime(details['release_date'], '%Y-%m-%d').year
            if details.get('belongs_to_collection'):
                refreshed['collection'] = details['belongs_to_collection']['name']
            for alt in alternatives['titles']:
                refreshed['title_%s' % alt['iso_3166_1'].lower()] = alt['title']
            return refreshed


class TmdbProxyDatasourceSchema(DefaultDatasourceSchema):

    base_url = Value(String())
    max_results = Value(Integer(min=1), default=None)


class TmdbProxyDatasource(Datasource):

    config_schema = TmdbProxyDatasourceSchema()

    def _get(self, uri, *args, **kwargs):
        url = self.config.get('base_url').rstrip('/') + uri
        for _ in xrange(3):
            printer.debug('Requesting {url}', url=url)
            response = requests.get(url, params=kwargs)
            if not 200 <= response.status_code < 400 :
                printer.debug('Got error ({http_err}), retrying in 3s...', http_err=response.status_code)
                time.sleep(3)
                continue
            return json.loads(response.text)
        else:
            raise KubrickRuntimeError('Unable to get the URL')

    def search(self, title):
        results = self._get('/1/search', query=title)['movies']
        if self.config.get('max_results') is not None:
            results = results[:self.config.get('max_results')]
        for result in results:
            movie = Movie(result)
            yield movie

    def refresh(self, movie):
        """ Try to refresh metadata of the movie through the datasource.
        """
        if '_tmdb_id' in movie:
            tmdb_id = movie['_tmdb_id']
            movie = self._get('/1/movie/%s' % tmdb_id)
            return movie['movie']
