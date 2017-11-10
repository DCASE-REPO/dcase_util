# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User interfacing
================

Utility classes for light user interfacing.

**FancyLogger** and **FancyPrinter** provide the same API, only difference is that
FancyLogger will output to the logging system and FancyPrinter uses standard print function to print the
output to sys.stdout. **FancyStringifier** can be used in general case when output is need in string form.

FancyLogger
-----------

*dcase_util.ui.FancyLogger*

This class provides extra formatting when using logging. If Python logging is not yet initialized when calling
FancyLogger, `dcase_util.utils.setup_logging` is first called.

Usage examples:

.. code-block:: python
    :linenos:

    ui = dcase_util.ui.FancyLogger()
    ui.title('title')
    ui.section_header('section_header')
    ui.sub_header('sub_header')
    ui.foot('foot')
    ui.line('line', indent=2)
    ui.line('line', indent=4)
    ui.line('line', indent=6)

    # Data row with field and value
    ui.data('data field', 'value', 'unit')

    # Horizontal separator
    ui.sep()

    # Table
    ui.table(cell_data=[[1, 2, 3], [1, 2, 3]])

    # Faster way to create output tables without collecting data into one data structure.
    ui.row('Header1', 'Header2', widths=[10,20], types=['float2','str20'])
    ui.row('-','-')
    ui.row(10.21231, 'String text')

Output::

    [I] title
    [I] section_header
    [I] ========================================
    [I] === sub_header ===
    [I]   foot
    [I]
    [I]   line
    [I]     line
    [I]       line
    [I]   data field                        : value unit
    [I] ========================================
    [I] Col #0   Col #1
    [I] ------   ------
    [I]      1        1
    [I]      2        2
    [I]      3        3
    [I]
    [I]   Header1 | Header2           |
    [I]   ------- | ----------------- |
    [I]    10.21  | String text       |

.. autosummary::
    :toctree: generated/

    FancyLogger
    FancyLogger.line
    FancyLogger.row
    FancyLogger.title
    FancyLogger.section_header
    FancyLogger.sub_header
    FancyLogger.foot
    FancyLogger.data
    FancyLogger.sep
    FancyLogger.table
    FancyLogger.info
    FancyLogger.debug
    FancyLogger.error

FancyPrinter
------------

*dcase_util.processors.FancyPrinter*

This class provides uniformly formatted status printing to the console.

Usage examples:

.. code-block:: python
    :linenos:

    ui = dcase_util.ui.FancyPrinter()
    ui.title('title')
    ui.section_header('section_header')
    ui.sub_header('sub_header')
    ui.foot('foot')
    ui.line('line', indent=2)
    ui.line('line', indent=4)
    ui.line('line', indent=6)

    # Data row with field and value
    ui.data('data field', 'value', 'unit')

    # Horizontal separator
    ui.sep()

    # Table
    ui.table(cell_data=[[1, 2, 3], [1, 2, 3]])

    # Faster way to create output tables without collecting data into one data structure.
    ui.row('Header1', 'Header2', widths=[10,20], types=['float2','str20'])
    ui.row('-','-')
    ui.row(10.21231, 'String text')

Output::

    title
    section_header
    ========================================
    === sub_header ===
      foot

      line
        line
          line
      data field                        : value unit
    ========================================
    Col #0   Col #1
    ------   ------
         1        1
         2        2
         3        3

      Header1 | Header2           |
      ------- | ----------------- |
       10.21  | String text       |

.. autosummary::
    :toctree: generated/

    FancyPrinter
    FancyPrinter.line
    FancyPrinter.row
    FancyPrinter.title
    FancyPrinter.section_header
    FancyPrinter.sub_header
    FancyPrinter.foot
    FancyPrinter.data
    FancyPrinter.sep
    FancyPrinter.table
    FancyPrinter.info
    FancyPrinter.debug
    FancyPrinter.error

FancyStringifier
----------------

*dcase_util.processors.FancyStringifier*

This class can be used to produce uniformly formatted output strings.

.. autosummary::
    :toctree: generated/

    FancyStringifier
    FancyStringifier.title
    FancyStringifier.section_header
    FancyStringifier.sub_header
    FancyStringifier.foot
    FancyStringifier.line
    FancyStringifier.formatted_value
    FancyStringifier.data
    FancyStringifier.sep
    FancyStringifier.table
    FancyStringifier.row
    FancyStringifier.class_name

"""

from .ui import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
