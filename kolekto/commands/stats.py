import os
from datetime import timedelta
from collections import defaultdict
from itertools import islice

from kolekto.commands import Command
from kolekto.datasources import MovieDatasource
from kolekto.printer import printer


SUFFIXES = ('KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')


def humanize_filesize(value):
    """ Return an humanized file size.
    """

    value = float(value)

    if value == 1:
        return '1 Byte'
    elif value < 1024:
        return '%d Bytes' % value
    elif value < 1024:
        return '%dB' % value

    for i, s in enumerate(SUFFIXES):
        unit = 1024 ** (i + 2)
        if value < unit:
            return '%.1f %s' % ((1024 * value / unit), s)
    return '%.1f %s' % ((1024 * value / unit), s)


def format_top(counter, top=3):
    """ Format a top.
    """
    items = islice(reversed(sorted(counter.iteritems(), key=lambda x: x[1])), 0, top)
    return u'; '.join(u'{g} ({nb})'.format(g=g, nb=nb) for g, nb in items)


class Stats(Command):

    """ Get stats about the movies collection.
    """

    help = 'get stats about the movie collection'

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)
        mds = MovieDatasource(config.subsections('datasource'), args.tree, self.profile.object_class)
        total_runtime = 0
        total_size = 0
        count_by_genre = defaultdict(lambda: 0)
        count_by_director = defaultdict(lambda: 0)
        count_by_quality = defaultdict(lambda: 0)
        count_by_container = defaultdict(lambda: 0)
        for movie_hash, movie in mdb.itermovies():
            movie_fullpath = os.path.join(args.tree, '.kolekto', 'movies', movie_hash)
            movie = mds.attach(movie_hash, movie)
            total_runtime += movie.get('runtime', 0)
            total_size += os.path.getsize(movie_fullpath)
            for genre in movie.get('genres', []):
                count_by_genre[genre] += 1
            for director in movie.get('directors', []):
                count_by_director[director] += 1
            count_by_quality[movie.get('quality', 'n/a')] += 1
            count_by_container[movie.get('container', 'n/a')] += 1

        printer.p('<b>Number of movies:</b>', mdb.count())
        printer.p('<b>Total runtime:</b>', timedelta(seconds=total_runtime * 60))
        printer.p('<b>Total size:</b>', humanize_filesize(total_size))
        printer.p('<b>Genres top3:</b>', format_top(count_by_genre))
        printer.p('<b>Director top3:</b>', format_top(count_by_director))
        printer.p('<b>Quality:</b>', format_top(count_by_quality, None))
        printer.p('<b>Container:</b>', format_top(count_by_container, None))