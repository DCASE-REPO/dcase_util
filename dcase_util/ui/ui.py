#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
import six
import logging
import numpy
import datetime
import re
from dcase_util.utils import setup_logging, is_float, is_int


class FancyStringifier(object):
    """Fancy UI
    """

    def __init__(self):
        self.row_column_widths = []
        self.row_data_types = []
        self.row_indent = 2
        self.row_column_separators = []
        self.row_column_count = None
        self.row_column_numerical_value_sum = {}
        self.row_column_numerical_value_count = {}

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    def title(self, text):
        """Title

        Parameters
        ----------
        text : str
            Title text

        Returns
        -------
        str

        """

        return text

    def section_header(self, text, indent=0):
        """Section header

        Parameters
        ----------
        text : str
            Section header text

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        str

        """

        return ' ' * indent + text + '\n' + self.sep(indent=indent)

    def sub_header(self, text='', indent=0):
        """Sub header

        Parameters
        ----------
        text : str, optional
            Footer text

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        str

        """

        return ' ' * indent + '=== ' + text + ' ==='

    def foot(self, text='DONE', time=None, item_count=None, indent=2):
        """Footer

        Parameters
        ----------
        text : str, optional
            Footer text
            Default value 'DONE'

        time : str or float, optional
            Elapsed time as string or float (as seconds)
            Default value None

        item_count : int, optional
            Item count
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 2

        Returns
        -------
        str

        """

        output = '{text:10s} '.format(text=text)

        if time:
            if isinstance(time, six.string_types):
                output += '[{time:<14s}] '.format(time=time)

            elif isinstance(time, float):
                output += '[{time:<14s}] '.format(time=str(datetime.timedelta(seconds=time)))

        if item_count:
            output += '[{items:<d} items] '.format(items=item_count)

            if time and isinstance(time, float):
                output += '[{item_time:<14s} per item]'.format(
                    item_time=str(datetime.timedelta(seconds=time / float(item_count)))
                )

        return ' ' * indent + output

    def line(self, field=None, indent=2):
        """Line

        Parameters
        ----------
        field : str
            Data field name
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 2

        Returns
        -------
        str

        """

        if field is not None:
            lines = field.split('\n')
        else:
            lines = ['']

        for line_id, line in enumerate(lines):
            lines[line_id] = ' ' * indent + '{field:}'.format(field=line)

        return '\n'.join(lines)

    @staticmethod
    def formatted_value(value, data_type='auto'):
        """Format value into string.

        Valid data_type parameters:

        - auto
        - str or stf (fixed width string, padded with white space)
        - bool
        - float1, float2, float3, float4
        - float1_percentage, float2_percentage, float3_percentage, float4_percentage
        - float1_percentage+ci, float2_percentage+ci, float3_percentage+ci, float4_percentage+ci
        - float1_ci, float2_ci, float3_ci, float4_ci
        - float1_ci_bracket, float2_ci_bracket, float3_ci_bracket, float4_ci_bracket

        Parameters
        ----------
        value :

        data_type : str
            Data type in format [type label][length], e.g. for floats with 4 decimals use 'float4',
            strings with fixed length 10 use 'str10'. For automatic value formatting use 'auto'.
            Default value 'auto'

        Returns
        -------
        str

        """

        if value is None:
            value = "None"

        if data_type == 'auto':
            if isinstance(value, bool):
                data_type = 'bool'

            elif isinstance(value, int):
                data_type = 'int'

            elif isinstance(value, float):
                data_type = 'float2'

            else:
                data_type = 'str'

        # Float
        if data_type == 'float1' and is_float(value):
            value = '{:.1f}'.format(float(value))

        elif data_type == 'float2' and is_float(value):
            value = '{:.2f}'.format(float(value))

        elif data_type == 'float3' and is_float(value):
            value = '{:.3f}'.format(float(value))

        elif data_type == 'float4' and is_float(value):
            value = '{:.4f}'.format(float(value))

        elif data_type == 'int' and is_int(value):
            value = '{:d}'.format(int(value))

        # Float (percentage)
        elif data_type == 'float1_percentage' and is_float(value):
            value = '{:3.1f}%'.format(float(value))

        elif data_type == 'float2_percentage' and is_float(value):
            value = '{:3.2f}%'.format(float(value))

        elif data_type == 'float3_percentage' and is_float(value):
            value = '{:3.3f}%'.format(float(value))

        elif data_type == 'float4_percentage' and is_float(value):
            value = '{:3.4f}%'.format(float(value))

        # Float (percentage) + confidence interval
        elif data_type == 'float1_percentage+ci' and isinstance(value, tuple):
            value = '{:3.1f}% (+/-{:3.1f})'.format(float(value[0]), float(value[1]))

        elif data_type == 'float2_percentage+ci' and isinstance(value, tuple):
            value = '{:3.2f}% (+/-{:3.2f})'.format(float(value[0]), float(value[1]))

        elif data_type == 'float3_percentage+ci' and isinstance(value, tuple):
            value = '{:3.3f}% (+/-{:3.3f})'.format(float(value[0]), float(value[1]))

        elif data_type == 'float4_percentage+ci' and isinstance(value, tuple):
            value = '{:3.4f}% (+/-{:3.4f})'.format(float(value[0]), float(value[1]))

        # Float + confidence interval
        elif data_type == 'float1+ci' and isinstance(value, tuple):
            value = '{:3.1f} (+/-{:3.1f})'.format(float(value[0]), float(value[1]))

        elif data_type == 'float2+ci' and isinstance(value, tuple):
            value = '{:3.2f} (+/-{:3.2f})'.format(float(value[0]), float(value[1]))

        elif data_type == 'float3+ci' and isinstance(value, tuple):
            value = '{:3.3f} (+/-{:3.3f})'.format(float(value[0]), float(value[1]))

        elif data_type == 'float4+ci' and isinstance(value, tuple):
            value = '{:3.4f} (+/-{:3.4f})'.format(float(value[0]), float(value[1]))

        # Float confidence interval
        elif data_type == 'float1_ci':
            value = '+/-{:3.1f}'.format(float(value))

        elif data_type == 'float2_ci':
            value = '+/-{:3.2f}'.format(float(value))

        elif data_type == 'float3_ci':
            value = '+/-{:3.3f}'.format(float(value))

        elif data_type == 'float4_ci':
            value = '+/-{:3.4f}'.format(float(value))

        # Float confidence interval bracket
        elif data_type == 'float1_ci_bracket' and isinstance(value, tuple):
            value = '{:3.1f}-{:3.1f}'.format(float(value[0]), float(value[1]))

        elif data_type == 'float2_ci_bracket' and isinstance(value, tuple):
            value = '{:3.2f}-{:3.2f}'.format(float(value[0]), float(value[1]))

        elif data_type == 'float3_ci_bracket' and isinstance(value, tuple):
            value = '{:3.3f}-{:3.3f}'.format(float(value[0]), float(value[1]))

        elif data_type == 'float4_ci_bracket' and isinstance(value, tuple):
            value = '{:3.4f}-{:3.4f}'.format(float(value[0]), float(value[1]))

        elif isinstance(value, numpy.ndarray):
            shape = value.shape

            if len(shape) == 1:
                value = 'array ({0:d},)'.format(shape[0])

            elif len(shape) == 2:
                value = 'matrix ({0:d},{1:d})'.format(shape[0], shape[1])

            elif len(shape) == 3:
                value = 'matrix ({0:d},{1:d},{2:d})'.format(shape[0], shape[1], shape[2])

            elif len(shape) == 4:
                value = 'matrix ({0:d},{1:d},{2:d},{3:d})'.format(shape[0], shape[1], shape[2], shape[3])

        elif data_type == 'bool':
            if value:
                value = 'True'

            else:
                value = 'False'

        elif data_type.startswith('str'):
            value = str(value)

            if len(data_type) > 3:
                value_width = int(data_type[3:])

                if value and len(value) > value_width:
                    value = value[0:value_width - 2] + '..'

        elif data_type.startswith('stf'):
            value = str(value)

            if len(data_type) > 3:
                value_width = int(data_type[3:])

                if value and len(value) > value_width:
                    value = value[0:value_width - 2] + '..'

                elif value and len(value) < value_width:
                    value = value.ljust(value_width)

        return value

    def data(self, field=None, value=None, unit=None, indent=2):
        """Data line

        Parameters
        ----------
        field : str
            Data field name
            Default value None

        value : str, bool, int, float, list or dict
            Data value
            Default value None

        unit : str
            Data value unit
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 2

        Returns
        -------
        str

        """

        mid = 35
        mid_point = str(mid - indent)
        line = '{field:<' + mid_point + '} : {value} {unit}'
        line2 = '{field:<' + mid_point + '}'

        value = self.formatted_value(value=value)

        lines = value.split('\n')
        if len(lines) > 1:
            # We have multi-line value, inject indent
            for i in range(1, len(lines)):
                lines[i] = ' ' * indent + ' ' * (mid-indent+3) + lines[i]

            value = '\n'.join(lines)

        if value is None or value == 'None':
            unit = None

        if field is not None and value is not None:
            return ' ' * indent + line.format(
                field=str(field),
                value=self.formatted_value(value),
                unit=str(unit) if unit else '',
            )

        elif field is not None and value is None:
            return ' ' * indent + line2.format(
                field=str(field)
            )

        elif field is None and value is not None:
            return ' ' * indent + line.format(
                field=' '*20,
                value=self.formatted_value(value),
                unit=str(unit) if unit else '',
            )

        else:
            return ' ' * indent

    def sep(self, length=40, indent=0):
        """Horizontal separator

        Parameters
        ----------
        length : int
            Length of separator
            Default value 40

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        str

        """

        return ' ' * indent + '=' * (length - indent)

    def table(self, cell_data=None, column_headers=None, column_types=None,
              column_separators=None, row_separators=None, indent=0):
        """Data table

        Parameters
        ----------
        cell_data : list of list
            Cell data in format [ [cell(col1,row1), cell(col1,row2), cell(col1,row3)],
            [cell(col2,row1), cell(col2,row2), cell(col2,row3)] ]
            Default value None

        column_headers : list of str
            Column headers in list, if None given column numbers are used
            Default value None

        column_types : list of str
            Column data types, if None given type is determined automatically.
            Possible values: ['int', 'float1', 'float2', 'float3', 'float4', 'str10', 'str20']]
            Default value None

        column_separators : list of int
            Column ids where to place separation lines. Line is placed on the right of the indicated column.
            Default value None

        row_separators : list of int
            Row ids where to place separation lines. Line is place after indicated row.
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        str

        """

        if cell_data is None:
            cell_data = []

        if column_headers is None:
            column_headers = []

        if column_types is None:
            column_types = []

        if column_separators is None:
            column_separators = []

        if row_separators is None:
            row_separators = []

        if len(cell_data) != len(column_headers):
            # Generate generic column titles
            for column_id, column_data in enumerate(cell_data):
                if column_id >= len(column_headers):
                    column_headers.append('Col #{:d}'.format(column_id))

        if len(cell_data) != len(column_types):
            # Generate generic column types
            for column_id, column_data in enumerate(cell_data):
                if column_id >= len(column_types) or column_types[column_id] == 'auto':
                    row_data = cell_data[column_id]

                    if all(isinstance(x, int) for x in row_data):
                        data_type = 'int'

                    elif all(isinstance(x, float) for x in row_data):
                        data_type = 'float2'

                    elif all(isinstance(x, six.string_types) for x in row_data):
                        data_type = 'str20'

                    else:
                        data_type = 'str20'

                    column_types.append(data_type)

        line_template = ""
        sep_column = []
        for column_id, (data, header, data_type) in enumerate(zip(cell_data, column_headers, column_types)):
            if data_type.startswith('str'):
                if len(data_type) > 3:
                    column_width = int(data_type[3:])

                else:
                    column_width = 10

                line_template += '{' + str(column_id) + ':<' + str(column_width) + 's} '

            elif data_type.startswith('float') or data_type.startswith('int'):
                column_width = 6
                if len(column_headers[column_id]) > column_width:
                    column_width = len(column_headers[column_id])
                line_template += '{' + str(column_id) + ':>'+str(column_width)+'s} '

            else:
                message = '{name}: Unknown column type [{data_type}].'.format(
                    name=self.__class__.__name__,
                    data_type=data_type
                )
                self.logger.exception(message)
                raise ValueError(message)

            if column_id in column_separators:
                line_template += '| '

            else:
                line_template += '  '

            sep_column.append('-' * column_width)

        output = ''
        output += ' '*indent + line_template.format(*column_headers) + '\n'
        output += ' '*indent + line_template.format(*sep_column) + '\n'

        for row_id, tmp in enumerate(cell_data[0]):
            row_data = []
            for column_id, (column_data, data_type) in enumerate(zip(cell_data, column_types)):
                cell_value = column_data[row_id]
                if data_type == 'auto':
                    if isinstance(cell_value, int):
                        data_type = 'int'

                    elif isinstance(cell_value, float):
                        data_type = 'float2'

                    elif isinstance(cell_value, six.string_types):
                        data_type = 'str10'

                    else:
                        data_type = 'str10'

                if data_type == 'float1' and is_float(cell_value):
                    row_data.append('{:6.1f}'.format(float(cell_value)))

                elif data_type == 'float2' and is_float(cell_value):
                    row_data.append('{:6.2f}'.format(float(cell_value)))

                elif data_type == 'float3' and is_float(cell_value):
                    row_data.append('{:6.3f}'.format(float(cell_value)))

                elif data_type == 'float4' and is_float(cell_value):
                    row_data.append('{:6.4f}'.format(float(cell_value)))

                elif data_type == 'int' and is_int(cell_value):
                    row_data.append('{:d}'.format(int(cell_value)))

                elif data_type.startswith('str'):
                    if len(data_type) > 3:
                        column_width = int(data_type[3:])
                    else:
                        column_width = 10

                    if cell_value is None:
                        cell_value = '-'

                    if cell_value and len(cell_value) > column_width:
                        cell_value = cell_value[0:column_width - 2] + '..'

                    row_data.append(cell_value)

                elif cell_value is None:
                    row_data.append('-')

            if row_id in row_separators:
                output += ' '*indent + line_template.format(*sep_column) + '\n'
            output += ' '*indent + line_template.format(*row_data) + '\n'

        return output

    def row(self, *args, **kwargs):
        """Table row

        Parameters
        ----------
        args : various
            Data for columns

        indent : int
            Amount of indention used for the row. If None given, value from previous method call is used.

        widths : list of int
            Column widths. If None given, value from previous method call is used.

        types : list of str
            Column data types, see `formatted_value` method more. If None given, value from previous
            method call is used.

        separators : list of bool
            Column vertical separators. If None given, value from previous method call is used.

        accumulate : bool
            Flag to indicate internal column wise value accumulation.
            Default value True

        Returns
        -------
        str

        """

        if kwargs.get('indent'):
            self.row_indent = kwargs.get('indent')

        if kwargs.get('widths'):
            self.row_column_widths = kwargs.get('widths')

        if kwargs.get('types'):
            self.row_data_types = kwargs.get('types')

        if kwargs.get('separators'):
            self.row_column_separators = kwargs.get('separators')

        accumulate = kwargs.get('accumulate', True)

        self.row_column_count = len(args)

        line_string = ''
        for column_id, column_data in enumerate(args):
            if column_id < len(self.row_column_widths):
                column_width = self.row_column_widths[column_id]
            else:
                column_width = 15

            if column_id < len(self.row_data_types):
                data_type = self.row_data_types[column_id]
            else:
                data_type = 'auto'

            column_width -= 3

            cell = ''
            if column_id > 0:
                cell += ' '

            cell += '{0:<' + str(column_width) + 's} '

            if accumulate:
                if (isinstance(column_data, int) or isinstance(column_data, float)):
                    if column_id not in self.row_column_numerical_value_count:
                        self.row_column_numerical_value_count[column_id] = 0

                    if column_id not in self.row_column_numerical_value_sum:
                        self.row_column_numerical_value_sum[column_id] = 0

                    self.row_column_numerical_value_count[column_id] += 1
                    self.row_column_numerical_value_sum[column_id] += column_data


            column_data = self.formatted_value(column_data, data_type=data_type)

            if isinstance(column_data, int):
                line_string += cell.format(str(column_data))

            elif isinstance(column_data, six.string_types):
                if len(column_data) > column_width and column_data != '-':
                    column_data = column_data[0:(column_width-2)] + '..'

                elif column_data == '-':
                    column_data = column_width * column_data[0]

                line_string += cell.format(str(column_data))

            elif column_data is None:
                line_string += cell.format(' ')

            if column_id < len(self.row_column_separators) and self.row_column_separators[column_id]:
                line_string += '|'

            else:
                line_string += ' '


        return ' ' * self.row_indent + line_string

    def row_reset(self):
        """Reset table row formatting

        Returns
        -------
        self

        """

        self.row_column_widths = []
        self.row_data_types = []
        self.row_indent = 2
        self.row_column_separators = []
        self.row_column_count = None
        self.row_value_cache_reset()

        return self

    def row_sep(self, separator_char='-'):
        """Table separator row

        Parameters
        ----------
        separator_char : str
            Character used for the separator row
            Default value '-'

        Returns
        -------
        str

        """

        row_list = []
        if self.row_column_count:
            for i in range(0, self.row_column_count):
                row_list.append(separator_char)

            return self.row(*row_list)

        else:
            return ''

    def row_sum(self, label='Sum'):
        """Table row showing internally accumulated sum of previous row values per column

        Parameters
        ----------
        label : str or dict
            Label used for non-accumulated columns. Can be dict where column id is key.
            Default value 'Sum'

        Returns
        -------
        str

        """

        values = []
        for column_id in range(0, self.row_column_count):
            if column_id in self.row_column_numerical_value_sum:
                values.append(self.row_column_numerical_value_sum[column_id])

            elif isinstance(label,dict) and column_id in label:
                values.append(label[column_id])

            else:
                values.append(label)

        return self.row(*values, accumulate=False)

    def row_average(self, label='Avg'):
        """Table row showing internally accumulated average of previous row values per column

        Parameters
        ----------
        label : str or dict
            Label used for non-accumulated columns. Can be dict where column id is key.
            Default value 'Avg'

        Returns
        -------
        str

        """

        values = []
        for column_id in range(0, self.row_column_count):
            if column_id in self.row_column_numerical_value_sum:
                values.append(
                    self.row_column_numerical_value_sum[column_id] / float(self.row_column_numerical_value_count[column_id])
                )

            elif isinstance(label,dict) and column_id in label:
                values.append(label[column_id])

            else:
                values.append(label)

        return self.row(*values, accumulate=False)

    def row_value_cache_reset(self):
        self.row_column_numerical_value_sum = {}
        self.row_column_numerical_value_count = {}

    def class_name(self, class_name, indent=0):
        """Class name

        Parameters
        ----------
        class_name : str
            Class name

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        str

        """

        return ' ' * indent + class_name + " :: Class"


class FancyHTMLStringifier(FancyStringifier):
    """Fancy UI to produce HTML output
    """

    def __init__(self):
        super(FancyHTMLStringifier, self).__init__()
        self.indent_factor = 10

        self.row_reset()
        self.row_highlight_flag = False
        self.row_highlight_style = 'background-color: #F1F1F166;'
        self.row_highlight_style_alt = 'background-color: #F9F9F966;'
        self.row_item_width_factor = 8

    def get_margin(self, indent=0, include_style_attribute=True):
        """Get margin css style definition

        Parameters
        ----------
        indent : int
            Amount of indention used for the line
            Default value 2

        include_style_attribute : bool
            Include "style=" in the returned string
            Default True

        Returns
        -------
        str

        """

        if include_style_attribute:
            return ' style="margin-left:' + str(indent * self.indent_factor) + 'px" '
        else:
            return 'margin-left:' + str(indent * self.indent_factor) + 'px;'

    def line(self, field=None, indent=2):
        """Line

        Parameters
        ----------
        field : str
            Data field name
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 2

        Returns
        -------
        str

        """

        indent_px = indent * self.indent_factor
        if field is not None:
            lines = field.split('\n')
        else:
            lines = ['&nbsp;']

        if self.row_highlight_flag:
            bg = self.row_highlight_style
        else:
            bg = ''

        html = ''
        for line_id, line in enumerate(lines):
            html += '<div class="row clearfix" style="' +bg + '">'

            html += '<div class="col-md-12" style="padding:2px;font-size:100%;font-weight:bold">'
            html += str(line)
            html += '</div>'

            html += '</div>'

        # Flip row highlighting flag
        self.row_highlight_flag = not self.row_highlight_flag

        return html

    def title(self, text, tag='h1'):
        """Title

        Parameters
        ----------
        text : str
            Title text

        tag : str
            HTML tag used for the title
            Default value "h1"

        Returns
        -------
        str

        """

        return '<' + tag + '>' + text + '</' + tag + '>' + '\n'

    def section_header(self, text, indent=0, tag='h2'):
        """Section header

        Parameters
        ----------
        text : str
            Section header text

        indent : int
            Amount of indention used for the line
            Default value 0

        tag : str
            HTML tag used for the title
            Default value "h2"

        Returns
        -------
        str

        """

        return '<' + tag + ' style="border-bottom: 2px solid #666;' + self.get_margin(
            indent=indent,
            include_style_attribute=False
        ) + '">' + text + '</' + tag + '>' + '\n'

    def sub_header(self, text='', indent=0, tag='h3'):
        """Sub header

        Parameters
        ----------
        text : str, optional
            Footer text

        indent : int
            Amount of indention used for the line
            Default value 0

        tag : str
            HTML tag used for the title
            Default value "h3"

        Returns
        -------
        str

        """

        return '<' + tag + self.get_margin(indent=indent) + '>' + text + '</' + tag + '>' + '\n'

    def sep(self, length=40, indent=0, height=4):
        """Horizontal separator

        Parameters
        ----------
        length : int
            Length of separator
            Default value 40

        indent : int
            Amount of indention used for the line
            Default value 0

        height : int
            Separator line height in pixels
            Default value 4

        Returns
        -------
        str

        """

        return '<hr style="' + self.get_margin(indent=indent,
                                               include_style_attribute=False) + 'border-top-width: ' + str(
            height) + 'px;background-color:transparent;" width="' + str(length) + '%">'

    def foot(self, text='DONE', time=None, item_count=None, indent=2):
        """Footer

        Parameters
        ----------
        text : str, optional
            Footer text
            Default value 'DONE'

        time : str or float, optional
            Elapsed time as string or float (as seconds)
            Default value None

        item_count : int, optional
            Item count
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 2

        Returns
        -------
        str

        """

        output = '{text:10s} '.format(text=text)

        if time:
            if isinstance(time, six.string_types):
                output += '[{time:<14s}] '.format(time=time)

            elif isinstance(time, float):
                output += '[{time:<14s}] '.format(time=str(datetime.timedelta(seconds=time)))

        if item_count:
            output += '[{items:<d} items] '.format(items=item_count)

            if time and isinstance(time, float):
                output += '[{item_time:<14s} per item]'.format(
                    item_time=str(datetime.timedelta(seconds=time / float(item_count)))
                )

        return '<div ' + self.get_margin(indent=indent) + '>' + output + '</div>'

    def data(self, field=None, value=None, unit=None, indent=2):
        """Data line

        Parameters
        ----------
        field : str
            Data field name
            Default value None

        value : str, bool, int, float, list or dict
            Data value
            Default value None

        unit : str
            Data value unit
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 2

        Returns
        -------
        str

        """

        value = self.formatted_value(value=value)

        if value is None or value == 'None':
            unit = None

        lines = value.split('\n')
        indent_px = indent * self.indent_factor

        if self.row_highlight_flag:
            bg = self.row_highlight_style
        else:
            bg = self.row_highlight_style_alt

        col1 = 'col-md-4 col-xs-6'
        col2 = 'col-md-8 col-xs-6'

        # Container
        html = ''
        html += '<div class="row row-no-gutters clearfix" '
        html += 'style="' + bg + '">'

        # Field
        html += '<div class="' + col1 + '" '
        html += 'style="padding-left:' + str(indent_px) + 'px;"'
        html += '>'
        html += str(field)
        html += '<span class="pull-right text-muted" style="padding-right:5px;">:</span>'
        html += '</div>'

        # Value + unit
        if len(lines) > 1:
            html += '<div class="' + col2 + '">'
            html += lines[0]
            html += '</div>'

            for i in range(1, len(lines)):
                html += '<div class="' + col1 + '"></div>'
                html += '<div class="' + col2 + '">'
                html += lines[i]
                html += '</div>'

        else:
            html += '<div class="' + col2 + '">'
            html += self.formatted_value(value) + ' '
            html += '<span class="text-muted">' + str(unit) + '</span>' if unit else ''
            html += '</div>'

        html += '</div>'  # Container

        # Flip row highlighting flag
        self.row_highlight_flag = not self.row_highlight_flag

        return html

    def row(self, *args, **kwargs):
        """Table row

        Parameters
        ----------
        args : various
            Data for columns

        indent : int
            Amount of indention used for the row. If None given, value from previous method call is used.

        widths : list of int
            Column widths. If None given, value from previous method call is used.

        types : list of str
            Column data types, see `formatted_value` method more. If None given, value from previous
            method call is used.

        separators : list of bool
            Column vertical separators. If None given, value from previous method call is used.

        Returns
        -------
        str

        """

        if kwargs.get('indent'):
            self.row_indent = kwargs.get('indent')

        if kwargs.get('widths'):
            self.row_column_widths = kwargs.get('widths')

        if kwargs.get('types'):
            self.row_data_types = kwargs.get('types')

        if kwargs.get('separators'):
            self.row_column_separators = kwargs.get('separators')

        self.row_column_count = len(args)

        if self.row_highlight_flag:
            bg = 'background-color: #EEE;'
        else:
            bg = ''

        html = ''
        grid_template_columns = []
        for column_id, column_data in enumerate(args):
            if column_id < len(self.row_column_widths):
                column_width = int(self.row_column_widths[column_id] * self.row_item_width_factor)
            else:
                column_width = int(15 * self.row_item_width_factor)

            grid_template_columns.append(str(column_width) + 'px')

        grid_template_columns = ' '.join(grid_template_columns)

        html += '<div style="'
        html += 'font-size: 110%;'
        html += 'display:grid;grid-template-columns:' + grid_template_columns + ';grid-gap:0px;'
        html += 'margin-top: -4px; margin-bottom: -4px;'
        html += self.get_margin(indent=self.row_indent, include_style_attribute=False)
        html += '">'

        for column_id, column_data in enumerate(args):
            if column_id < len(self.row_data_types):
                data_type = self.row_data_types[column_id]
            else:
                data_type = 'auto'

            if column_id < len(self.row_column_widths):
                column_width = int(self.row_column_widths[column_id] * self.row_item_width_factor)
            else:
                column_width = int(15 * self.row_item_width_factor)

            column_data = self.formatted_value(column_data, data_type=data_type)

            if column_id < len(self.row_column_separators) and self.row_column_separators[column_id]:
                sep = 'border-right: 2px solid #333;'
            else:
                sep = ''

            html += '<div style="padding:2px;' + bg + sep + '">'
            if isinstance(column_data, int):
                html += str(column_data)

            elif isinstance(column_data, six.string_types):
                if len(column_data) > column_width and column_data != '-':
                    column_data = column_data[0:(column_width - 2)] + '..'

                elif column_data == '-':
                    column_data = column_width * column_data[0]

                html += str(column_data)

            html += '</div>'

        html += '</div>'  # Container

        # Flip row highlighting flag
        self.row_highlight_flag = not self.row_highlight_flag

        return html

    def row_reset(self):
        """Reset table row formatting

        Returns
        -------
        self

        """

        self.row_highlight_flag = False
        self.row_column_widths = []
        self.row_data_types = []
        self.row_indent = 0
        self.row_column_separators = []
        self.row_column_count = None

        return self

    def row_sep(self, **kwargs):
        """Table separator row

        Returns
        -------
        str

        """

        html = ''

        grid_template_columns = []
        for column_id in range(0, self.row_column_count):
            if column_id < len(self.row_column_widths):
                column_width = int(self.row_column_widths[column_id] * self.row_item_width_factor)

            else:
                column_width = int(15 * self.row_item_width_factor)

            grid_template_columns.append(str(column_width) + 'px')

        grid_template_columns = ' '.join(grid_template_columns)
        html += '<div style="'
        html += 'display:grid;grid-template-columns:' + grid_template_columns + ';grid-gap:0px;'
        html += 'margin-top:-4px;margin-bottom:-3px;height:2px;' + self.get_margin(
            indent=self.row_indent, include_style_attribute=False
        )
        html += '">'

        for i in range(0, self.row_column_count):
            html += '<div style="padding:0px;margin:0px;background-color:#333;">'
            html += '</div>'

        html += '</div>'  # Container

        return html

    def table(self, cell_data=None, column_headers=None, column_types=None,
              column_separators=None, row_separators=None, indent=0, scaling=110, table_css_class='table-striped table-condensed'):
        """Data table

        Parameters
        ----------
        cell_data : list of list
            Cell data in format [ [cell(col1,row1), cell(col1,row2), cell(col1,row3)],
            [cell(col2,row1), cell(col2,row2), cell(col2,row3)] ]
            Default value None

        column_headers : list of str
            Column headers in list, if None given column numbers are used
            Default value None

        column_types : list of str
            Column data types, if None given type is determined automatically.
            Possible values: ['int', 'float1', 'float2', 'float3', 'float4', 'str10', 'str20']]
            Default value None

        column_separators : list of int
            Column ids where to place separation lines. Line is placed on the right of the indicated column.
            Default value None

        row_separators : list of int
            Row ids where to place separation lines. Line is place after indicated row.
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 0

        scaling : int
            Percentage to change the size of the table
            Default value None

        table_css_class : str
            CSS classes to be added to the resulting table
            Default value "table-striped table-condensed"

        Returns
        -------
        str

        """

        if cell_data is None:
            cell_data = []

        if column_headers is None:
            column_headers = []

        if column_types is None:
            column_types = []

        if column_separators is None:
            column_separators = []

        if row_separators is None:
            row_separators = []

        if len(cell_data) != len(column_headers):
            # Generate generic column titles
            for column_id, column_data in enumerate(cell_data):
                if column_id >= len(column_headers):
                    column_headers.append('Col #{:d}'.format(column_id))

        if len(cell_data) != len(column_types):
            # Generate generic column types
            for column_id, column_data in enumerate(cell_data):
                if column_id >= len(column_types) or column_types[column_id] == 'auto':
                    row_data = cell_data[column_id]

                    if all(isinstance(x, int) for x in row_data):
                        data_type = 'int'

                    elif all(isinstance(x, float) for x in row_data):
                        data_type = 'float2'

                    elif all(isinstance(x, six.string_types) for x in row_data):
                        data_type = 'str20'

                    else:
                        data_type = 'str20'

                    column_types.append(data_type)

        thead = '<thead style="border-bottom: 0px solid transparent;">'
        thead += '<tr>'
        for column_id, (data, header, data_type) in enumerate(zip(cell_data, column_headers, column_types)):
            align = 'text-align:right;'
            if data_type.startswith('str'):
                if len(data_type) > 3:
                    column_width = int(data_type[3:])

                else:
                    column_width = 8
                align = 'text-align:left;'

            elif data_type.startswith('float') or data_type.startswith('int'):
                column_width = 6
                if len(column_headers[column_id]) > column_width:
                    column_width = len(column_headers[column_id])

            else:
                message = '{name}: Unknown column type [{data_type}].'.format(
                    name=self.__class__.__name__,
                    data_type=data_type
                )
                self.logger.exception(message)
                raise ValueError(message)

            sep = 'border-bottom:2px solid #333;'
            if column_id in column_separators:
                sep += 'border-right:2px solid #333;'

            thead += '<th style="width:' + str(column_width * 10) + 'px;' + sep + align + '">'

            thead += column_headers[column_id]
            thead += '</th>'

        thead += '</tr>'
        thead += '</thead>'

        html = ''
        html += '<table class="table '+table_css_class+'" style="font-size:'+str(scaling)+'%;width:auto;margin-top:0em;' + self.get_margin(
            indent=indent,
            include_style_attribute=False
        ) + '">'

        html += thead
        html += '<tbody>'

        for row_id, tmp in enumerate(cell_data[0]):
            html += '<tr>'

            for column_id, (column_data, data_type) in enumerate(zip(cell_data, column_types)):
                align = 'text-align:right;'
                if data_type.startswith('str'):
                    align = 'text-align:left;'

                style = ''
                if row_id in row_separators:
                    style += 'border-top:2px solid #333;'

                if column_id in column_separators:
                    style += 'border-right:2px solid #333;'

                html += '<td style="' + style + align + '">'

                cell_value = column_data[row_id]
                if data_type == 'auto':
                    if isinstance(cell_value, int):
                        data_type = 'int'

                    elif isinstance(cell_value, float):
                        data_type = 'float2'

                    elif isinstance(cell_value, six.string_types):
                        data_type = 'str10'

                    else:
                        data_type = 'str10'

                if data_type == 'float1' and is_float(cell_value):
                    html += '{:6.1f}'.format(float(cell_value))

                elif data_type == 'float2' and is_float(cell_value):
                    html += '{:6.2f}'.format(float(cell_value))

                elif data_type == 'float3' and is_float(cell_value):
                    html += '{:6.3f}'.format(float(cell_value))

                elif data_type == 'float4' and is_float(cell_value):
                    html += '{:6.4f}'.format(float(cell_value))

                elif data_type == 'int' and is_int(cell_value):
                    html += '{:d}'.format(int(cell_value))

                elif data_type.startswith('str'):
                    if len(data_type) > 3:
                        column_width = int(data_type[3:])
                    else:
                        column_width = 10

                    if cell_value is None:
                        cell_value = '-'

                    cell_value_stripped = re.sub(re.compile('<.*?>'), '', cell_value)
                    if cell_value and len(cell_value_stripped) > column_width:
                        cell_value = cell_value[0:column_width - 2] + '..'

                    html += cell_value

                elif cell_value is None:
                    html += '-'

                html += '</td>'
            html += '</tr>'

        html += '</tbody>'
        html += '</table>'

        return html

    def class_name(self, class_name, indent=0):
        """Class name

        Parameters
        ----------
        class_name : str
            Class name

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        str

        """

        return '<div class="label label-primary" ' \
               'style="margin-bottom:5px;margin-top:5px;display:inline-block;' + self.get_margin(
            indent=indent, include_style_attribute=False) + '">' + class_name + '</div>'


class FancyLogger(object):
    """Logger class
    """
    def __init__(self):
        """Constructor

        Parameters
        ----------

        Returns
        -------

        nothing

        """
        self.ui = FancyStringifier()

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()

        return logger

    def line(self, data='', indent=0, level='info'):
        """Generic line logger
        Multiple lines are split and logged separately

        Parameters
        ----------
        data : str or list, optional
            String or list of strings

        indent : int
            Amount of indention used for the line

        level : str
            Logging level, one of [info, debug, warning, warn, error]

        Returns
        -------
        nothing

        """

        if isinstance(data, six.string_types):
            lines = data.split('\n')

        elif isinstance(data, list):
            lines = data

        else:
            message = '{name}: Unknown data type [{data}].'.format(
                name=self.__class__.__name__,
                data=data
            )
            self.logger.exception(message)
            raise ValueError(message)

        for line in lines:
            if level.lower() == 'info':
                self.logger.info(' ' * indent + line)
            elif level.lower() == 'debug':
                self.logger.debug(' ' * indent + line)
            elif level.lower() == 'warning' or level.lower() == 'warn':
                self.logger.warn(' ' * indent + line)
            elif level.lower() == 'error':
                self.logger.error(' ' * indent + line)
            else:
                self.logger.info(' ' * indent + line)

    def row(self, *args, **kwargs):
        """Table row

        Parameters
        ----------
        args : various
            Data for columns

        indent : int
            Amount of indention used for the row. If None given, value from previous method call is used.

        widths : list of int
            Column widths. If None given, value from previous method call is used.

        types : list of str
            Column data types, see `formatted_value` method more. If None given, value from previous
            method call is used.

        separators : list of bool
            Column vertical separators. If None given, value from previous method call is used.

        Returns
        -------
        nothing

        """

        self.line(
            self.ui.row(*args, **kwargs)
        )

    def row_reset(self):
        """Reset table row formatting

        Returns
        -------
        nothing

        """

        self.ui.row_reset()

    def row_sep(self, separator_char='-'):
        """Table separator row

        Parameters
        ----------
        separator_char : str
            Character used for the separator row
            Default value '-'

        Returns
        -------
        nothing

        """

        self.line(
            self.ui.row_sep(separator_char=separator_char)
        )

    def row_sum(self, label='Sum'):
        """Table row showing internally accumulated sum of previous row values per column

        Parameters
        ----------
        label : str or dict
            Label used for non-accumulated columns. Can be dict where column id is key.
            Default value 'Sum'

        Returns
        -------
        str

        """
        self.line(
            self.ui.row_sum(label)
        )

    def row_average(self, label='Avg'):
        """Table row showing internally accumulated average of previous row values per column

        Parameters
        ----------
        label : str or dict
            Label used for non-accumulated columns. Can be dict where column id is key.
            Default value 'Avg'

        Returns
        -------
        str

        """
        self.line(
            self.ui.row_average(label)
        )

    def title(self, text, level='info'):
        """Title, logged at info level

        Parameters
        ----------
        text : str
            Title text

        level : str
            Logging level, one of [info, debug, warning, warn, error]
            Default value 'info'

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.title
        dcase_util.ui.FancyPrinter.title

        """

        self.line(
            self.ui.title(
                text=text
            ),
            level=level
        )

    def section_header(self, text, indent=0, level='info'):
        """Section header, logged at info level

        Parameters
        ----------
        text : str
            Section header text

        indent : int
            Amount of indention used for the line
            Default value 0

        level : str
            Logging level, one of [info, debug, warning, warn, error]
            Default value 'info'

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.section_header
        dcase_util.ui.FancyPrinter.section_header

        """

        self.line(
            self.ui.section_header(
                text=text,
                indent=indent
            ),
            level=level
        )

    def sub_header(self, text='', indent=0, level='info'):
        """Sub header

        Parameters
        ----------
        text : str, optional
            Footer text

        indent : int
            Amount of indention used for the line
            Default value 0

        level : str
            Logging level, one of [info, debug, warning, warn, error]
            Default value 'info'

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.sub_header
        dcase_util.ui.FancyPrinter.sub_header

        """

        self.line(
            self.ui.sub_header(
                text=text,
                indent=indent
            ),
            level=level
        )

    def foot(self, text='DONE', time=None, item_count=None, indent=2, level='info'):
        """Footer, logged at info level

        Parameters
        ----------
        text : str, optional
            Footer text.
            Default value 'DONE'

        time : str, optional
            Elapsed time as string.
            Default value None

        item_count : int, optional
            Item count.
            Default value None

        indent : int
            Amount of indention used for the line.
            Default value 2

        level : str
            Logging level, one of [info, debug, warning, warn, error].
            Default value 'info'

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.foot
        dcase_util.ui.FancyPrinter.foot

        """

        self.line(
            self.ui.foot(
                text=text,
                time=time,
                item_count=item_count,
                indent=indent
            ),
            level=level
        )
        self.line(level=level)

    def data(self, field=None, value=None, unit=None, indent=2, level='info'):
        """Data line logger

        Parameters
        ----------
        field : str
            Data field name
            Default value None

        value : str, bool, int, float, list or dict
            Data value
            Default value None

        unit : str
            Data value unit
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 2

        level : str
            Logging level, one of [info,debug,warning,warn,error]
            Default value 'info'

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.data
        dcase_util.ui.FancyPrinter.data

        """

        self.line(
            self.ui.data(
                field=field,
                value=value,
                unit=unit,
                indent=indent
            ),
            level=level
        )

    def sep(self, level='info', length=40, indent=0):
        """Horizontal separator, logged at info level

        Parameters
        ----------
        level : str
            Logging level, one of [info,debug,warning,warn,error]
            Default value 'info'

        length : int
            Length of separator
            Default value 40

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.sep
        dcase_util.ui.FancyPrinter.sep

        """

        self.line(
            self.ui.sep(
                length=length,
                indent=indent
            ),
            level=level
        )

    def table(self, cell_data=None, column_headers=None, column_types=None, column_separators=None,
              row_separators=None, indent=0, level='info'):
        """Data table

        Parameters
        ----------
        cell_data : list of list
            Cell data in format [ [cell(col1,row1), cell(col1,row2), cell(col1,row3)],
            [cell(col2,row1), cell(col2,row2), cell(col2,row3)] ]
            Default value None

        column_headers : list of str
            Column headers in list, if None given column numbers are used
            Default value None

        column_types : list of str
            Column data types, if None given type is determined automatically.
            Possible values: ['int', 'float1', 'float2', 'float3', 'float4', 'str10', 'str20']]
            Default value None

        column_separators : list of int
            Column ids where to place separation lines. Line is placed on the right of the indicated column.
            Default value None

        row_separators : list of int
            Row ids where to place separation lines. Line is place after indicated row.
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 0

        level : str
            Logging level, one of [info,debug,warning,warn,error]
            Default value 'info'

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.table
        dcase_util.ui.FancyPrinter.table

        """

        self.line(
            self.ui.table(
                cell_data=cell_data,
                column_headers=column_headers,
                column_types=column_types,
                column_separators=column_separators,
                row_separators=row_separators,
                indent=indent
            ),
            level=level
        )

    def info(self, text='', indent=0):
        """Info line logger

        Parameters
        ----------
        text : str
            Text
            Default value ''

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        nothing

        """

        self.line(
            data=text,
            level='info',
            indent=indent
        )

    def debug(self, text='', indent=0):
        """Debug line logger

        Parameters
        ----------
        text : str
            Text
            Default value ''

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        nothing

        """

        self.line(
            data=text,
            level='debug',
            indent=indent
        )

    def error(self, text='', indent=0):
        """Error line logger

        Parameters
        ----------
        text : str
            Text
            Default value ''

        indent : int
            Amount of indention used for the line
            Default value 0

        Returns
        -------
        nothing

        """

        self.line(
            data=text,
            level='error',
            indent=indent
        )


class FancyPrinter(FancyLogger):
    """Printer class
    """

    def __init__(self, colors=True):
        """Constructor

        Parameters
        ----------
        colors : bool
            Using colors or not
            Default value True

        Returns
        -------
        nothing

        """

        super(FancyPrinter, self).__init__()

        self.colors = colors

        self.levels = {
            'info': '',
            'debug': '',
            'warning': '',
            'warn': '',
            'error': '',
        }

        if self.colors:
            try:
                from colorama import init
                from colorama import Fore, Back, Style

            except ImportError:
                message = '{name}: Unable to import colorama module. You can install it with `pip install colorama`.'.format(
                    name=self.__class__.__name__
                )

                self.logger.exception(message)
                raise ImportError(message)

            init()
            self.levels['reset'] = Style.RESET_ALL
            self.levels['info'] = Style.NORMAL
            self.levels['debug'] = Fore.YELLOW
            self.levels['warning'] = Fore.MAGENTA
            self.levels['warn'] = Fore.MAGENTA
            self.levels['error'] = Back.RED + Fore.WHITE + Style.BRIGHT

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()

        return logger

    def line(self, data='', indent=0, level='info'):
        """Generic line logger
        Multiple lines are split and logged separately

        Parameters
        ----------
        data : str or list, optional
            String or list of strings
            Default value ''

        indent : int
            Amount of indention used for the line
            Default value 0

        level : str
            Logging level, one of [info, debug, warning, warn, error]
            Default value 'info'

        Returns
        -------
        nothing

        """

        if isinstance(data, six.string_types):
            lines = data.split('\n')

        elif isinstance(data, list):
            lines = data

        else:
            message = '{name}: Unknown data type [{data}].'.format(
                name=self.__class__.__name__,
                data=data
            )
            self.logger.exception(message)
            raise ValueError(message)

        for line in lines:
            if level in self.levels:
                print(' ' * indent + self.levels[level] + line + self.levels['reset'])

            else:
                print(' ' * indent + line)


class FancyHTMLPrinter(FancyLogger):
    """Printer class for rich HTML formatted output in IPython/Jupyter
    """

    def __init__(self, colors=True):
        """Constructor

        Parameters
        ----------
        colors : bool
            Using colors or not
            Default value True

        Returns
        -------
        nothing

        """

        super(FancyHTMLPrinter, self).__init__()

        self.ui = FancyHTMLStringifier()

        self.colors = colors

        self.levels = {
            'info': None, 
            'debug': 'alert alert-block alert-info',
            'warning': 'alert alert-block alert-warning',
            'warn': 'alert alert-block alert-warning',
            'error': 'alert alert-block alert-danger',
        }

    def line(self, data='', indent=0, level='info'):
        """Generic line logger
        Multiple lines are split and logged separately

        Parameters
        ----------
        data : str or list, optional
            String or list of strings
            Default value ''

        indent : int
            Amount of indention used for the line
            Default value 0

        level : str
            Logging level, one of [info, debug, warning, warn, error]
            Default value 'info'

        Returns
        -------
        nothing

        """
        from IPython.core.display import display, HTML

        if isinstance(data, six.string_types):
            lines = data.split('\n')

        elif isinstance(data, list):
            lines = data

        else:
            message = '{name}: Unknown data type [{data}].'.format(
                name=self.__class__.__name__,
                data=data
            )
            self.logger.exception(message)
            raise ValueError(message)

        for line in lines:
            if line:
                if level in self.levels and self.levels[level]:
                    display(HTML('<div class="'+self.levels[level]+'">' + line + '</div>'))

                else:
                    display(HTML(line))

    def table(self, cell_data=None, column_headers=None, column_types=None, column_separators=None,
              row_separators=None, indent=0, level='info', scaling=110, table_css_class='table-striped table-condensed'):
        """Data table

        Parameters
        ----------
        cell_data : list of list
            Cell data in format [ [cell(col1,row1), cell(col1,row2), cell(col1,row3)],
            [cell(col2,row1), cell(col2,row2), cell(col2,row3)] ]
            Default value None

        column_headers : list of str
            Column headers in list, if None given column numbers are used
            Default value None

        column_types : list of str
            Column data types, if None given type is determined automatically.
            Possible values: ['int', 'float1', 'float2', 'float3', 'float4', 'str10', 'str20']]
            Default value None

        column_separators : list of int
            Column ids where to place separation lines. Line is placed on the right of the indicated column.
            Default value None

        row_separators : list of int
            Row ids where to place separation lines. Line is place after indicated row.
            Default value None

        indent : int
            Amount of indention used for the line
            Default value 0

        level : str
            Logging level, one of [info,debug,warning,warn,error]
            Default value 'info'

        scaling : int
            Percentage to change the size of the table
            Default value None

        table_css_class : str
            CSS classes to be added to the resulting table
            Default value "table-striped table-condensed"

        Returns
        -------
        nothing

        See Also
        --------
        dcase_util.ui.FancyUI.table
        dcase_util.ui.FancyPrinter.table

        """

        self.line(
            self.ui.table(
                cell_data=cell_data,
                column_headers=column_headers,
                column_types=column_types,
                column_separators=column_separators,
                row_separators=row_separators,
                indent=indent,
                scaling=scaling,
                table_css_class=table_css_class
            ),
            level=level
        )
