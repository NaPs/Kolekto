import re

from kolekto.datasources import Datasource, DefaultDatasourceSchema

from confiture.schema.containers import Value, Section, many
from confiture.schema.types import String, Boolean


class LazyEval(String):

    """ A string base type evaluating string as Python expression lazily.

    Example in configuration::

        sum = 'sum(range(3, 10))'

    .. warning::
        This type can be dangerous since any Python expression can be typed
        by the user, like __import__("sys").exit(). Use it at your own risk.

    """

    def validate(self, value):
        value = super(LazyEval, self).validate(value)
        def _eval(locals=None, globals=None):
            return eval(value, globals, locals)
        return _eval


class FieldSection(Section):

    _meta = {'repeat': many, 'unique': True, 'args': Value(String())}
    value = Value(LazyEval())
    ignore_error = Value(Boolean(), default=False)


class RewriteDatasourceSchema(DefaultDatasourceSchema):

    rewrite = FieldSection()


class RewriteDatasource(Datasource):

    """ A datasource allowing to rewrite fields.
    """

    config_schema = RewriteDatasourceSchema()

    def __init__(self, *args, **kwargs):
        super(RewriteDatasource, self).__init__(*args, **kwargs)
        self.rewrites = [(x.args, x.get('value'), x.get('ignore_error'))
                         for x in self.config.subsections('rewrite')]

    def attach(self, movie_hash, movie):
        for field, rewrite_func, ignore_error in self.rewrites:
            try:
                value = rewrite_func(globals={'movie': movie, 'sub': re.sub,
                                              'split': re.split})
            except:
                if not ignore_error:
                    raise
            else:
                if value:
                    movie[field] = value
        return movie