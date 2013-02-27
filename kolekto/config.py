""" Kolekto configuration parsers.
"""

from dotconf import Dotconf
from dotconf.schema.containers import Section, Value
from dotconf.schema.types import String


class ViewKolektoConfig(Section):

    _meta = {'args': Value(String()),
             'unique': True,
             'repeat': (0, None)}

    pattern = Value(String())


class DatasourceKolektoConfig(Section):

    _meta = {'args': Value(String()),
             'unique': True,
             'repeat': (0, None),
             'allow_unknown': True}


class RootKolektoConfig(Section):

    view = ViewKolektoConfig()
    datasource = DatasourceKolektoConfig()


def parse_config(filename):
    conf = Dotconf.from_filename(filename, schema=RootKolektoConfig())
    return conf.parse()
