import os

import jinja2

from kolekto.commands import Command
from kolekto.exceptions import KolektoRuntimeError
from kolekto.pattern import parse_pattern
from kolekto.datasources import MovieDatasource


LISTING_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ title }}</title>
    <meta charset="UTF-8">
    <style>
        a {color: #666;}
    </style>
</head>
<body>

<table id="movies">
    <thead>
        <tr>
        {% for column, props in columns %}
            <th>{{ column }}</th>
        {% endfor %}
        </tr>
    </thead>
    <tbody>
    {% for filename, movie, movie_columns in movies %}
        <tr>
        {% for column in movie_columns %}
            {% if columns[loop.index0][1].get('link') %}
            <td><a download="{{ movie.title }}.{{ movie.ext }}" href="{{ filename }}#{{ movie.title }}">{{ column }}</a></td>
            {% else %}
            <td>{{ column }}</td>
            {% endif %}
        {% endfor %}
        </tr>
    {% endfor %}
        </tr>
    </tbody>
</table>

<script src="tablefilter/tablefilter.js"></script>

<script data-config>
    var filtersConfig = {
    {% for column, props in columns %}
        col_{{ loop.index0 }}: '{{ props.get('filter_type') }}',
    {% endfor %}
        alternate_rows: true,
        loader: true,
        col_date_type: [{% for column, props in columns %}{% if props.get('is_date') %}'DMY'{% else %}null{% endif %}, {% endfor %}],
        extensions:[{ name: 'sort' }]
    };
    var tf = new TableFilter('movies', filtersConfig);
    tf.init();
</script>

<div style="text-align: right; color: #AAA; font-style: italic; padding: 5px;">
{{ credits }}
</div>

</body>
</html>'''


class WebExportFormatWrapper(object):

    """ A wrapper used to customize how movies attributes are formatted.
    """

    def __init__(self, title, obj):
        self.title = title
        self.obj = obj

    def __unicode__(self):
        if isinstance(self.obj, bool):
            if self.obj:
                return self.title.title()
        elif isinstance(self.obj, list):
            if not self.obj:
                return 'None'  # List is empty
            elif len(self.obj) > 1:
                return ', '.join(self.obj)
            else:
                return unicode(self.obj[0])
        else:
            return unicode(self.obj)

    def __repr__(self):
        return repr(self.obj)


class WebExport(Command):

    """ Export movies list to a web page.
    """

    help = 'export movies listing in a web page'

    def prepare(self):
        self.add_arg('webexport', metavar='webexport', default='default', nargs='?')
        self.add_arg('destination', metavar='destination')
        self.add_arg('-p', '--pool-path', default='movies', help='Public path to movies pool')

    def _config(self, args, config):
        """ Get configuration for the current used listing.
        """
        webexports = dict((x.args, x) for x in config.subsections('webexport'))
        webexport = webexports.get(args.webexport)
        if webexport is None:
            if args.webexport == u'default':
                raise NotImplementedError('Default webexport not implemented')  # FIXME
            else:
                raise KolektoRuntimeError('Unknown webexport %r' % args.webexport)
        else:
            return {'columns': list(webexport.subsections('column')),
                    'page_title': webexport.get('page_title'),
                    'page_credits': webexport.get('page_credits')}

    def run(self, args, config):
        mdb = self.get_metadata_db(args.tree)
        mds = MovieDatasource(config.subsections('datasource'), args.tree, self.profile.object_class)
        webexport = self._config(args, config)
        columns = [(x.args, x) for x in webexport['columns']]
        movies = []

        for movie_hash, movie in sorted(mdb.itermovies(), key=lambda x: x[1].get('title')):
            filename = os.path.join(args.pool_path, movie_hash)
            movie_columns = []
            movie = mds.attach(movie_hash, movie)
            for column in webexport['columns']:
                prepared_env = parse_pattern(column.get('pattern'), movie, WebExportFormatWrapper)
                movie_columns.append(column.get('pattern').format(**prepared_env))
            movies.append((filename, movie, movie_columns))

        template = jinja2.Template(LISTING_TEMPLATE)
        with open(args.destination, 'w') as fdest:
            fdest.write(template.render(columns=columns,
                                        movies=movies,
                                        title=webexport['page_title'],
                                        credits=webexport['page_credits']).encode('utf8'))
