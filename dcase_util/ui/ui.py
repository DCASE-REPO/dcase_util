#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
import logging
import numpy
from dcase_util.utils import setup_logging, is_float, is_int


class FancyStringifier(object):
    """Fancy UI
    """

    def __init__(self):
        self.row_column_widths = []
        self.row_data_types = []
        self.row_indent = 2
        self.row_column_separators = []

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
            title string

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

        Returns
        -------
        str
            section header string

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

        Returns
        -------
        str
            Sub header string

        """

        return ' ' * indent + '=== ' + text + ' ==='

    def foot(self, text='DONE', time=None, item_count=None, indent=2):
        """Footer

        Parameters
        ----------
        text : str, optional
            Footer text

        time : str, optional
            Elapsed time as string

        item_count : int, optional
            Item count

        indent : int
            Amount of indention used for the line

        Returns
        -------
        str
            footer string

        """

        output = '{text:10s} '.format(text=text)

        if time:
            output += '[{time:<15s}] '.format(time=time)

        if item_count:
            output += '[{items:<d} items] '.format(items=item_count)

        return ' ' * indent + output

    def line(self, field=None, indent=2):
        """Line

        Parameters
        ----------
        field : str
            Data field name

        indent : int
            Amount of indention used for the line

        Returns
        -------
        str

        """
        lines = field.split('\n')

        for line_id, line in enumerate(lines):
            lines[line_id] = ' ' * indent + '{field:}'.format(field=line)

        return '\n'.join(lines)

    def formatted_value(self, value, data_type='auto'):
        """Format value into string.

        Parameters
        ----------
        value :

        data_type : str
            Data type in format [type label][length], e.g. for floats with 4 decimals use 'float4',
            strings with fixed length 10 use 'str10'. For automatic value formatting use 'auto'.

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

        elif data_type == 'float1_percentage' and is_float(value):
            value = '{:3.1f}%'.format(float(value))

        elif data_type == 'float2_percentage' and is_float(value):
            value = '{:3.2f}%'.format(float(value))

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

                value = value

        return value

    def data(self, field=None, value=None, unit=None, indent=2):
        """Data line

        Parameters
        ----------
        field : str
            Data field name

        value : str, bool, int, float, list or dict
            Data value

        unit : str
            Data value unit

        indent : int
            Amount of indention used for the line

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

        indent : int
            Amount of indention used for the line

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

        column_headers : list of str
            Column headers in list, if None given column numbers are used

        column_types : list of str
            Column data types, if None given type is determined automatically.
            Possible values: ['int', 'float1', 'float2', 'float3', 'float4', 'str10', 'str20']]

        column_separators : list of int
            Column ids where to place separation lines. Line is placed on the right of the indicated column.

        row_separators : list of int
            Row ids where to place separation lines. Line is place after indicated row.

        indent : int
            Amount of indention used for the line

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

                    elif all(isinstance(x, str) for x in row_data):
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

                    elif isinstance(cell_value, str):
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

            column_data = self.formatted_value(column_data, data_type=data_type)

            if isinstance(column_data, int):
                line_string += cell.format(str(column_data))

            elif isinstance(column_data, str):
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

    def class_name(self, class_name):
        """Class name

        Parameters
        ----------
        class_name : str
            Class name

        Returns
        -------
        str

        """

        return class_name + " :: Class"


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

        if isinstance(data, str):
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
        self.line(
            self.ui.row(*args, **kwargs)
        )

    def title(self, text, level='info'):
        """Title, logged at info level

        Parameters
        ----------
        text : str
            Title text

        level : str
            Logging level, one of [info, debug, warning, warn, error]

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

        level : str
            Logging level, one of [info, debug, warning, warn, error]


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

        level : str
            Logging level, one of [info, debug, warning, warn, error]

        Returns
        -------
        str
            Sub header string

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

        time : str, optional
            Elapsed time as string.

        item_count : int, optional
            Item count.

        indent : int
            Amount of indention used for the line.

        level : str
            Logging level, one of [info, debug, warning, warn, error].


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

        value : str, bool, int, float, list or dict
            Data value

        unit : str
            Data value unit

        indent : int
            Amount of indention used for the line

        level : str
            Logging level, one of [info,debug,warning,warn,error]

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

        length : int
            Length of separator

        indent : int
            Amount of indention used for the line

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

        column_headers : list of str
            Column headers in list, if None given column numbers are used

        column_types : list of str
            Column data types, if None given type is determined automatically.
            Possible values: ['int', 'float1', 'float2', 'float3', 'float4', 'str10', 'str20']]

        column_separators : list of int
            Column ids where to place separation lines. Line is placed on the right of the indicated column.

        row_separators : list of int
            Row ids where to place separation lines. Line is place after indicated row.

        indent : int
            Amount of indention used for the line

        level : str
            Logging level, one of [info,debug,warning,warn,error]


        Returns
        -------
        str

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

        indent : int
            Amount of indention used for the line


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

        indent : int
            Amount of indention used for the line

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

        indent : int
            Amount of indention used for the line

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
            from colorama import init
            from colorama import Fore, Back, Style
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

        indent : int
            Amount of indention used for the line

        level : str
            Logging level, one of [info, debug, warning, warn, error]

        Returns
        -------
        nothing

        """

        if isinstance(data, str):
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

