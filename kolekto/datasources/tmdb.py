""" The moviedb database for Kolekto.
"""

import json
import requests
import time
from datetime import datetime

from kolekto.printer import printer
from kolekto.datasources import Datasource, DefaultDatasourceSchema
from kolekto.exceptions import KolektoRuntimeError

from confiture.schema.containers import Value
from confiture.schema.types import String, Integer


requests_session = requests.Session()


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
        response = requests_session.get(url.encode('utf8'))
        return json.loads(response.text)

    def _get(self, url, *args, **kwargs):
        ak = self.config.get('api_key')
        url = url % dict(api_key=ak, **kwargs)
        for _ in xrange(3):
            printer.debug('Requesting {url}', url=url)
            response = requests.get(url)
            if not response.ok:
                printer.debug('Got error ({http_err}), retrying in 3s...', http_err=response.status_code)
                time.sleep(3)
                continue
            return json.loads(response.text)
        else:
            err_msg = 'Unable to get the URL, server reported error: %s' % response.status_code
            # Show the error reason message to the user if the requests
            # version is sufficiently recent:
            if hasattr(response, 'reason'):
                err_msg += ' (%s)' % response.reason
            raise KolektoRuntimeError(err_msg)

    def _tmdb_get(self, movie_id):
        return self._get(self.URL_GET, id=movie_id)

    def _tmdb_cast(self, movie_id):
        return self._get(self.URL_CAST, id=movie_id)

    def _tmdb_alt(self, movie_id):
        return self._get(self.URL_ALT, id=movie_id)

    def search(self, title, year=None):
        results = self._tmdb_search(title)['results']
        max_results = self.config.get('max_results')
        for result in results:
            # Abort the search if max results is reached:
            if max_results == 0:
                break

            # Parse the release year:
            if result.get('release_date'):
                movie_year = datetime.strptime(result['release_date'], '%Y-%m-%d').year
            else:
                movie_year = None

            # Skip the movie if searched date is not the release date:
            if year is not None and year != movie_year:
                continue

            # Else, format and yield the movie:
            cast = self._tmdb_cast(result['id'])
            movie = self.object_class({'title': result['original_title'],
                                       'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing'],
                                       '_datasource': self.name,
                                       '_tmdb_id': result['id']})
            if movie_year:
                movie['year'] = movie_year
            yield movie

            if max_results is not None:
                max_results -= 1

    def refresh(self, movie):
        """ Try to refresh metadata of the movie through the datasource.
        """
        if '_tmdb_id' in movie:
            tmdb_id = movie['_tmdb_id']
            details = self._tmdb_get(tmdb_id)
            cast = self._tmdb_cast(tmdb_id)
            alternatives = self._tmdb_alt(tmdb_id)
            refreshed = self.object_class({'title': details['original_title'],
                                           'score': details['popularity'],
                                           'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing'],
                                           'writers': [x['name'] for x in cast['crew'] if x['department'] == 'Writing'],
                                           'cast': [x['name'] for x in cast['cast']],
                                           'genres': [x['name'] for x in details['genres']],
                                           'countries': [x['name'] for x in details['production_countries']],
                                           'tmdb_votes': int(round(details.get('vote_average', 0) * 0.5)),
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
            response = requests_session.get(url, params=kwargs)
            if not response.ok :
                printer.debug('Got error ({http_err}), retrying in 3s...', http_err=response.status_code)
                time.sleep(3)
                continue
            return json.loads(response.text)
        else:
            err_msg = 'Unable to get the URL, server reported error: %s' % response.status_code
            # Show the error reason message to the user if the requests
            # version is sufficiently recent:
            if hasattr(response, 'reason'):
                err_msg += ' (%s)' % response.reason
            raise KolektoRuntimeError(err_msg)

    def search(self, title, year=None):
        results = self._get('/1/search', query=title)['movies']
        max_results = self.config.get('max_results')

        for result in results:
            # Abort the search if max results is reached:
            if max_results == 0:
                break

            # Skip the movie if searched date is not the release date:
            if year is not None and year != result.get('year'):
                continue

            movie = self.object_class(result)
            yield movie

            if max_results is not None:
                max_results -= 1

    def refresh(self, movie):
        """ Try to refresh metadata of the movie through the datasource.
        """
        if '_tmdb_id' in movie:
            tmdb_id = movie['_tmdb_id']
            movie = self._get('/1/movie/%s' % tmdb_id)
            return movie['movie']
