""" This module provide a small TMDB proxy.
"""

import os
import json
from datetime import datetime

import requests
import redis

from flask import Flask, Response, request


TMDB_API_URL = u'http://api.themoviedb.org/3'
ONE_WEEK = 604800


app = Flask(__name__)
app.config.update(REDIS_HOST=os.environ.get('KUBRICK_REDIS_HOST', 'localhost'),
                  REDIS_PORT=int(os.environ.get('KUBRICK_REDIS_PORT', 6379)),
                  REDIS_DB=int(os.environ.get('KUBRICK_REDIS_DB', 0)),
                  TMDB_API_KEY=os.environ['KUBRICK_TMDB_API_KEY'],
                  CACHE_TTL=int(os.environ.get('KUBRICK_CACHE_TTL', ONE_WEEK)),
                  DEBUG=os.environ.get('KUBRICK_DEBUG') == 'on')

redis_conn = redis.StrictRedis(host=app.config['REDIS_HOST'],
                               port=app.config['REDIS_PORT'],
                               db=app.config['REDIS_DB'])
requests_session = requests.Session()


def get_on_tmdb(uri, **kwargs):
    """ Get a resource on TMDB.
    """
    kwargs['api_key'] = app.config['TMDB_API_KEY']
    response = requests_session.get((TMDB_API_URL + uri).encode('utf8'), params=kwargs)
    return json.loads(response.text)


@app.route('/1/search')
def search():
    """ Search a movie on TMDB.
    """
    redis_key = 's_%s' % request.args['query'].lower()
    cached = redis_conn.get(redis_key)
    if cached:
        return Response(cached)
    else:
        found = get_on_tmdb(u'/search/movie', query=request.args['query'])
        movies = []
        for movie in found['results']:
            cast = get_on_tmdb(u'/movie/%s/casts' % movie['id'])
            year = None if movie['release_date'] is None else datetime.strptime(movie['release_date'], '%Y-%m-%d').year
            movies.append({'title': movie['original_title'],
                           'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing'],
                           'year': year,
                           '_tmdb_id': movie['id']})
        json_response = json.dumps({'movies': movies})
        redis_conn.setex(redis_key, app.config['CACHE_TTL'], json_response)
        return Response(json_response)


@app.route('/1/movie/<int:tmdb_id>')
def get_movie(tmdb_id):
    """ Get informations about a movie using its tmdb id.
    """
    redis_key = 'm_%s' % tmdb_id
    cached = redis_conn.get(redis_key)
    if cached:
        return Response(cached)
    else:
        details = get_on_tmdb(u'/movie/%d' % tmdb_id)
        cast = get_on_tmdb(u'/movie/%d/casts' % tmdb_id)
        alternative = get_on_tmdb(u'/movie/%d/alternative_titles' % tmdb_id)
        movie = {'title': details['original_title'],
                 'score': details['popularity'],
                 'directors': [x['name'] for x in cast['crew'] if x['department'] == 'Directing'],
                 'writers': [x['name'] for x in cast['crew'] if x['department'] == 'Writing'],
                 'cast': [x['name'] for x in cast['cast']],
                 'genres': [x['name'] for x in details['genres']],
                 'countries': [x['name'] for x in details['production_countries']],
                 '_tmdb_id': tmdb_id}
        if details.get('release_date'):
            movie['year'] = datetime.strptime(details['release_date'], '%Y-%m-%d').year
        if details.get('belongs_to_collection'):
            movie['collection'] = details['belongs_to_collection']['name']
        for alt in alternative['titles']:
            movie['title_%s' % alt['iso_3166_1'].lower()] = alt['title']
        json_response = json.dumps({'movie': movie})
        redis_conn.setex(redis_key, app.config['CACHE_TTL'], json_response)
        return Response(json_response)


if __name__ == '__main__':
    app.run()