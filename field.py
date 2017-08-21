from __future__ import print_function, unicode_literals, absolute_import
"""utilities for working with fields in a table or featureclass
"""

import arcpy
from arcutils.output import output_msg

def get_max_field_value_length(inputTable, field):
    """Return the length of the maximum value in the field.
        inputTable {String}:
            Path or reference to feature class or table.

        field {String}:
            name of the field to parse

        :return integer
    """
    length = 0
    with arcpy.da.SearchCursor(inputTable, field) as values:
            for value in values:
                if len(value[0]) > length:
                    length = len(value[0])
    return length


def get_field_value_set(inputTable, field, charset='ascii'):
    """Return a set of unique field values given an input table,
       a field name string and an optional charset (default='ascii')
       ascii charset will force encoding with ignore option.

        inputTable {String}:
            Path or reference to feature class or table.

        field {String}:
            name of the field to parse

        charset {String}:
            character set to use (default = 'ascii').
            Valid values are those in the Python documentation for string encode.
        :return set of unique values
       """

    try:
        value_set = set() # set to hold unique values
        with arcpy.da.SearchCursor(inputTable, field) as values:
            for value in values:
                if value[0] is None:
                    value_set.add("")
                elif isinstance(value[0], (str, unicode)):
                    if charset != 'ascii':
                        value_set.add(value[0])
                    else:
                        # if unicode strings are causing problem, try
                        value_set.add(value[0].encode('ascii', 'ignore'))
                else:
                    value_set.add(value[0])

        return value_set

    except arcpy.ExecuteError:
        output_msg(arcpy.GetMessages(2))
    except Exception as e:
        output_msg(e.args[0])




