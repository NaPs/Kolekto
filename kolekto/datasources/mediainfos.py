import os

from kolekto.datasources import Datasource

import kaa.metadata


class MediainfosDatasource(Datasource):

    def attach(self, movie_hash, movie):
        filename = os.path.join(self.tree, '.kolekto', 'movies', movie_hash)
        infos = kaa.metadata.parse(filename)
        if infos is None:
            return movie

        movie['container'] = infos['type'].strip()

        # Set the quality of the video depending on its definition:
        if infos.video[0].width < 1280:
            movie['quality'] = 'SD'
        elif 1280 <= infos.video[0].width < 1920:
            movie['quality'] = '720p'
        else:
            movie['quality'] = '1080p'

        # Set the file extension depending on its mimetype:
        movie['ext'] = infos['mime'].split('/')[-1]

        # Set the movie length (in minutes)
        movie['runtime'] = int(infos['length'] / 60)

        return movie
