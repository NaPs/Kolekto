""" Kubrick configuration parsers.
"""

from dotconf import Dotconf
from dotconf.schema.containers import Section, Value
from dotconf.schema.types import String


class ViewKubrickConfig(Section):

    _meta = {'args': Value(String()),
             'unique': True,
             'repeat': (0, None)}

    pattern = Value(String())


class DatasourceKubrickConfig(Section):

    _meta = {'args': Value(String()),
             'unique': True,
             'repeat': (0, None),
             'allow_unknown': True}


class RootKubrickConfig(Section):

    view = ViewKubrickConfig()
    datasource = DatasourceKubrickConfig()


def parse_config(filename):
    conf = Dotconf.from_filename(filename, schema=RootKubrickConfig())
    return conf.parse()
