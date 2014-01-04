""" Parse and format patterns.
"""

from string import Formatter


def parse_pattern(format_string, env, wrapper=lambda x, y: y):
    """ Parse the format_string and return prepared data according to the env.

    Pick each field found in the format_string from the env(ironment), apply
    the wrapper on each data and return a mapping between field-to-replace and
    values for each.
    """

    formatter = Formatter()
    fields = [x[1] for x in formatter.parse(format_string) if x[1] is not None]

    prepared_env = {}

    # Create a prepared environment with only used fields, all as list:
    for field in fields:
        # Search for a movie attribute for each alternative field separated
        # by a pipe sign:
        for field_alt in (x.strip() for x in field.split('|')):
            # Handle default values (enclosed by quotes):
            if field_alt[0] in '\'"' and field_alt[-1] in '\'"':
                field_values = field_alt[1:-1]
            else:
                field_values = env.get(field_alt)
            if field_values is not None:
                break
        else:
            field_values = []
        if not isinstance(field_values, list):
            field_values = [field_values]
        prepared_env[field] = wrapper(field_alt, field_values)

    return prepared_env
