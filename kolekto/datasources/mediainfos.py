import os
import logging

from kolekto.datasources import Datasource
from kolekto.helpers import JsonDbm

import kaa.metadata


# Configure the kaa.metadata logger in order to silent it:
metadata_logger = logging.getLogger('metadata')
metadata_logger.setLevel(logging.CRITICAL)


class MediainfosDatasource(Datasource):

    def __init__(self, *args, **kwargs):
        super(MediainfosDatasource, self).__init__(*args, **kwargs)
        # Open the media infos cache:
        cache_filename = os.path.join(self.tree, '.kolekto', 'media-info-cache.db')
        self._cache = JsonDbm(cache_filename)

    def attach(self, movie_hash, movie):
        if movie_hash in self._cache:
            media_infos = self._cache.get(movie_hash)
        else:
            filename = os.path.join(self.tree, '.kolekto', 'movies', movie_hash)
            infos = kaa.metadata.parse(filename)
            if infos is None:
                return movie

            media_infos = {}
            media_infos['container'] = infos['type'].strip()

            # Set the quality of the video depending on its definition:
            if infos.video[0].width < 1280:
                media_infos['quality'] = 'SD'
            elif 1280 <= infos.video[0].width < 1920:
                media_infos['quality'] = '720p'
            else:
                media_infos['quality'] = '1080p'

            # Set the file extension depending on its mimetype:
            media_infos['ext'] = infos['mime'].split('/')[-1]

            # Set the movie length (in minutes)
            media_infos['runtime'] = int(infos['length'] / 60)
            self._cache.save(movie_hash, media_infos)

        movie.update(media_infos)
        return movie
