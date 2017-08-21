from __future__ import print_function, unicode_literals, absolute_import
"""utilities for working with tables, featureclasses and fields
"""

import arcpy
from arcutils.output import output_msg
from arcutils.output import get_valid_output_path


class TableObj(object):
    """ provide methods for working with a table/featureclass
    Usage: tbl = arcutils.table.TableObj(path)
    attributes:
        path: a string representing an table/featureclass
    """
    def __init__(self, table_path):
        """ sets up reference to table
        adds methods
        """
        self.path = table_path
        self.field_name_list = self.list_field_names(self.path)
        self.upper_field_name_dict = self._make_field_dict(self.path)


    def list_field_names(inputTable):
        """Return an array of field names given an input table.

            inputTable{String}:
                Path or reference to feature class or table.
            :return array of field names
        """
        f_list = []
        for f in arcpy.ListFields(inputTable):
            f_list.append(f.name)

        return f_list


    def make_field_dict(input_fc, ignore_fields=None, skip_shape=True):
        """return a dictionary of fields containing name normalized to upper case, type, length with the option to skip shape fields

        input_fc {String}:
                Path or reference to feature class or table.
        ignore_fields {Array}:
                Array of strings containing field names to ignore. Default is None
        skip_shape {Boolean}:
                Boolean to skip shape fields or not; Default is True
        :return dictionary of field name: attributes
        """
        if ignore_fields is None:
            fields_to_ignore = []
        else:
            fields_to_ignore = ignore_fields

        if skip_shape:
            fields_to_ignore.extend(["SHAPE", "SHAPE_AREA", "SHAPE.AREA", "SHAPE.STAREA()", "SHAPE_LENGTH", "SHAPE.LEN",
                                     "SHAPE.STLENGTH()"])

        l_fields = arcpy.ListFields(input_fc)
        field_dict = dict()
        for field in l_fields:
            if field.name.upper() not in fields_to_ignore:
                # return all strings as UPPER CASE
                field_dict[field.name.upper()] = [field.name, field.type.upper(), field.length]
        return field_dict


def pprint_fields(table):
    """ pretty print a table's fields and their properties

        inputTable {String}:
            Path or reference to feature class or table.
    """
    def _print(l):
        print("".join(["{:>12}".format(i) for i in l]))

    atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
            'editable', 'isNullable', 'length', 'precision',
            'required', 'scale',]
    _print(atts)

    for f in arcpy.ListFields(table):
        _print(["{:>12}".format(getattr(f, i)) for i in atts])


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


def get_tsv_field_info(table):
    """ Create a tsv output of a table's fields and their properties

        inputTable {String}:
            Path or reference to feature class or table.
        return string of tsv values
    """
    atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
            'editable', 'isNullable', 'length', 'precision',
            'required', 'scale',]

    str_output = "\t".join(["{}".format(i) for i in atts])
    str_output += "\n"
    for f in arcpy.ListFields(table):
        str_output += "\t".join(["{}".format(getattr(f, i)) for i in atts])
        str_output += "\n"
    return str_output


def list_field_names(inputTable):
    """Return an array of field names given an input table.

        inputTable{String}:
            Path or reference to feature class or table.
        :return array of field names
    """
    f_list = []
    for f in arcpy.ListFields(inputTable):
        f_list.append(f.name)

    return f_list


def make_field_dict(input_fc, ignore_fields=None, skip_shape=True):
    """return a dictionary of fields containing name normalized to upper case, type, length with the option to skip shape fields

    input_fc {String}:
            Path or reference to feature class or table.
    ignore_fields {Array}:
            Array of strings containing field names to ignore. Default is None
    skip_shape {Boolean}:
            Boolean to skip shape fields or not; Default is True
    :return dictionary of field name: attributes
    """
    if ignore_fields is None:
        fields_to_ignore = []
    else:
        fields_to_ignore = ignore_fields

    if skip_shape:
        fields_to_ignore.extend(["SHAPE", "SHAPE_AREA", "SHAPE.AREA", "SHAPE.STAREA()", "SHAPE_LENGTH", "SHAPE.LEN", "SHAPE.STLENGTH()"])

    l_fields=arcpy.ListFields(input_fc)
    field_dict = dict()
    for field in l_fields:
        if field.name.upper() not in fields_to_ignore:
            # return all strings as UPPER CASE
            field_dict[field.name.upper()] = [field.name, field.type.upper(), field.length]
    return field_dict


def compare_table_schemas(tbl1, tbl2):
    """compare the schemas of two tables. Return an array of results.

    table1 {String}:
            Path or reference to feature class or table.
    table2 {String}:
            Path or reference to feature class or table.
    :return array of results (field not found, field same, etc)
    """
    result_arr= []
    field_dict1 = make_field_dict(tbl1)
    field_dict2 = make_field_dict(tbl2)
    for ifield in sorted(list(set(field_dict1.keys()+field_dict2.keys()))):
        # check name for missing fields first
        if not (field_dict1.has_key(ifield)):
            the_result = " {0} not found in {1}".format(ifield, tbl1)
            output_msg(the_result)
            result_arr.append(the_result)
        elif not (field_dict2.has_key(ifield)):
            the_result = " {0} not found in {1}".format(ifield, tbl2)
            output_msg(the_result)
            result_arr.append(the_result)
        else:
            # string comparison of name, type and length
            if field_dict1[ifield] == field_dict2[ifield]:
                the_result = " {0} field same in both".format(ifield)
                output_msg(the_result)
            else:
                field_one_type = field_dict1[ifield][1]
                field_two_type = field_dict2[ifield][1]
                field_one_length = field_dict1[ifield][2]
                field_two_length = field_dict2[ifield][2]

                the_result = " {0} {1} {2} {3} does not exactly match {4} {5} {6} {7}".format(tbl1, ifield, field_one_type, field_one_length, tbl2, ifield, field_two_type, field_two_length)
                output_msg(the_result)
                result_arr.append(the_result)

    return result_arr


def report_fields_to_csv_schema(featureclass):
    """Create a csv schema report of all fields in a featureclass,
    to the base directory or user folder.

    featureclass {String}:
        path or reference to a featureclass.
    """
    import datetime
    import os

    start_time = datetime.datetime.today()
    start_date_string = start_time.strftime('%Y%m%d')
    default_env = arcpy.env.workspace
    fc = featureclass
    # nice to convert reported types to types accepted by add field tool
    type_conversions = {"String": "TEXT", "Float": "FLOAT", "Double": "DOUBLE", "SmallInteger": "SHORT", "Integer": "LONG", "Date": "DATE", "Blob": "BLOB", "Ratser": "RASTER", "GUID": "GUID", "TRUE": "True", "FALSE": "False"}

    try:
        output_msg("Processing: {}".format(fc))
        try:
            desc = arcpy.Describe(fc)
        except:
            raise ValueError("{} not found".format(fc))
        arcpy.env.workspace = fc

        report_dir = get_valid_output_path(desc.Path)

        log_file_name = desc.baseName + "_Field_Report " + start_date_string + ".csv"
        log_file_path = os.path.join(report_dir, log_file_name)
        output_msg("Report file: {0}".format(log_file_path))
        with open(log_file_path, "w") as logFile:
            logFile.write("FieldName,FieldType,FieldPrecision,FieldScale,FieldLength,FieldAlias,isNullable,Required,FieldDomain,")
            logFile.write("DefaultValue,Editable,BaseName")
            logFile.write("\n")

            try:
                fields = arcpy.ListFields(fc)
                for field in fields:
                    output_msg("Writing {}".format(field.name))
                    logFile.write('"{0}","{1}",{2},{3},{4},"{5}",{6},{7},"{8}",{9},{10},"{11}"\n'.format(
                        field.name,
                        type_conversions[field.type],
                        field.precision,
                        field.scale,
                        field.length,
                        field.aliasName,
                        type_conversions[field.isNullable],
                        type_conversions[field.required],
                        field.domain,
                        field.defaultValue,
                        type_conversions[field.editable],
                        field.baseName))
            except Exception as e:
                output_msg(str(e.args[0]))
                output_msg(arcpy.GetMessages())

    except Exception as e:
        output_msg(str(e.args[0]))
        output_msg(arcpy.GetMessages())
    finally:
        output_msg("Completed")
        arcpy.env.workspace = default_env


def convert_csv_schema_to_table(csv_file, table_name):
    # load the csv file
    # assume headers
    # ignore OBJECTID, SHAPE
    fields_to_ignore =["OBJECTID", "FID", "SHAPE", "SHAPE_AREA", "SHAPE.AREA", "SHAPE.STAREA()", "SHAPE_LENGTH", "SHAPE.LEN", "SHAPE.STLENGTH()"]
    # arcpy.AddField_management(in_table, field_name, field_type, {field_precision}, {field_scale}, {field_length}, {field_alias}, {field_is_nullable}, {field_is_required}, {field_domain})
    pass