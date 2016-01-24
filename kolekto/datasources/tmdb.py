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
                                       'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing' and x['job'] == 'Director'],
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
                                           'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing' and x['job'] == 'Director'],
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


class TmdbTVSeriesDatasource(Datasource):

    config_schema = TmdbDatasourceSchema()

    URL_SEARCH = (u'http://api.themoviedb.org/3/search/tv?api_key=%(api_key)s&query=%(query)s')
    URL_SERIES = u'http://api.themoviedb.org/3/tv/%(id)s?api_key=%(api_key)s'
    URL_SEASON = u'http://api.themoviedb.org/3/tv/%(id)s/season/%(season)s?api_key=%(api_key)s'
    URL_EPISODE = u'http://api.themoviedb.org/3/tv/%(id)s/season/%(season)s/episode/%(ep)s?api_key=%(api_key)s'
    URL_CREDITS = u'http://api.themoviedb.org/3/tv/%(id)s/season/%(season)s/episode/%(ep)s/credits?api_key=%(api_key)s'
    URL_ALT = u'http://api.themoviedb.org/3/tv/%(id)s/alternative_titles?api_key=%(api_key)s'

    def _tmdb_search(self, title):
        ak = self.config.get('api_key')
        url = self.URL_SEARCH % dict(api_key=ak, query=requests.utils.quote(title.encode('utf8')))
        response = requests_session.get(url.encode('utf8'))
        return json.loads(response.text)

    def _get(self, url, *args, **kwargs):
        ak = self.config.get('api_key')
        raise_on_404 = kwargs.pop('raise_on_404', False)
        url = url % dict(api_key=ak, **kwargs)
        for _ in xrange(3):
            printer.debug('Requesting {url}', url=url)
            response = requests.get(url)
            if raise_on_404 and response.status_code == 404:
                response.raise_for_status()
            elif not response.ok:
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

    def _tmdb_series(self, tvseries_id):
        return self._get(self.URL_SERIES, id=tvseries_id)

    def _tmdb_alt_titles(self, tvseries_id):
        return self._get(self.URL_ALT, id=tvseries_id)

    def _tmdb_season(self, tvseries_id, season):
        return self._get(self.URL_SEASON, id=tvseries_id, season=season)

    def _tmdb_episode(self, tvseries_id, season, episode):
        try:
            return self._get(self.URL_EPISODE, raise_on_404=True, id=tvseries_id, season=season, ep=episode)
        except requests.HTTPError:
            return None

    def _tmdb_credits(self, tvseries_id, season, episode):
        return self._get(self.URL_CREDITS, id=tvseries_id, season=season, ep=episode)

    def search(self, title, season=None, episode=None):
        results = self._tmdb_search(title)['results']
        max_results = self.config.get('max_results')
        for result in results:
            # Abort the search if max results is reached:
            if max_results == 0:
                break

            result_data = {'title': result['original_name'],
                           '_datasource': self.name,
                           '_tmdbtv_id': result['id']}

            # Add informations related to episode if requested:
            if season and episode:
                found = self._tmdb_episode(result['id'], season, episode)
                if found is None:
                    continue  # No episode where found for this series
                else:
                    result_data['episode_title'] = found['name']
                    result_data['season'] = found['season_number']
                    result_data['episode'] = found['episode_number']
                    result_data['_tmdbtv_id'] = result['id']

            yield self.object_class(result_data)

            if max_results is not None:
                max_results -= 1

    def refresh(self, movie):
        """ Try to refresh metadata of the movie through the datasource.
        """
        if '_tmdbtv_id' in movie:
            refreshed = {'_Datasource': self.name}
            tvseries_id = movie['_tmdbtv_id']
            series = self._tmdb_series(tvseries_id)
            alternatives = self._tmdb_alt_titles(tvseries_id)
            refreshed.update({'title': series['original_name'],
                              'year': datetime.strptime(series['first_air_date'], '%Y-%m-%d').year,
                              'genres': [x['name'] for x in series['genres']],
                              'networks': [x['name'] for x in series['networks']],
                              'countries': series['origin_country'],
                              'tmdb_votes': int(round(series.get('vote_average', 0) * 0.5))})
            for alt in alternatives['results']:
                refreshed['title_%s' % alt['iso_3166_1'].lower()] = alt['title']
            if 'season' in movie:
                season_num = movie['season']
                season = self._tmdb_season(tvseries_id, season_num)
                refreshed.update({'season_title': season['name']})
                if 'episode' in movie:
                    episode_num = movie['episode']
                    episode = self._tmdb_episode(tvseries_id, season_num, episode_num)
                    credits = self._tmdb_credits(tvseries_id, season_num, episode_num)
                    refreshed.update({'episode_title': episode['name'],
                                      'directors': [x['name'] for x in credits['crew'] if x['department'] == 'Directing' and x['job'] == 'Director'],
                                      'writers': [x['name'] for x in credits['crew'] if x['department'] == 'Writing'],
                                      'cast': [x['name'] for x in credits['cast']],
                                      'guests': [x['name'] for x in credits['guest_stars']]})
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
