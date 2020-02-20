#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import sys
import logging
import logging.config
import yaml
from dcase_util.decorators import RunOnce


@RunOnce
def setup_logging(parameters=None,
                  coloredlogs=False,
                  logging_file=None,
                  default_setup_file='logging.yaml',
                  default_level=logging.INFO,
                  environmental_variable='LOG_CFG'):
    """Setup logging configuration

    Parameters
    ----------
    parameters : dict
        Parameters in dict
        Default value None

    coloredlogs : bool
        Use coloredlogs
        Default value False

    logging_file : str
        Log filename for file based logging, if none given no file logging is used.
        Default value None

    environmental_variable : str
        Environmental variable to get the logging setup filename, if set will override default_setup_file
        Default value 'LOG_CFG'

    default_setup_file : str
        Default logging parameter file, used if one is not set in given ParameterContainer
        Default value 'logging.yaml'

    default_level : logging.level
        Default logging level, used if one is not set in given ParameterContainer
        Default value 'logging.INFO'

    Returns
    -------
    nothing

    """

    class LoggerFilter(object):
        def __init__(self, level):
            self.__level = level

        def filter(self, log_record):
            return log_record.levelno <= self.__level

    formatters = {
        'simple': "[%(levelname).1s] %(message)s",
        'normal': "%(asctime)s\t[%(name)-20s]\t[%(levelname)-8s]\t%(message)s",
        'extended': "[%(asctime)s] [%(name)s]\t [%(levelname)-8s]\t %(message)s \t(%(filename)s:%(lineno)s)",
        'extended2': "[%(levelname).1s] %(message)s \t(%(filename)s:%(lineno)s)",
        'file_extended': "[%(levelname).1s] [%(asctime)s] %(message)s",
    }

    if not parameters:
        logging_parameter_file = default_setup_file

        value = os.getenv(environmental_variable, None)
        if value:
            # If environmental variable set
            logging_parameter_file = value

        if os.path.exists(logging_parameter_file):
            with open(logging_parameter_file, 'rt') as f:
                config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

            try:
                # Check if coloredlogs is available
                import coloredlogs
                coloredlogs.install(
                    level=config['handlers']['console']['level'],
                    fmt=config['formatters'][config['handlers']['console']['formatter']]['format']
                )

            except ImportError:
                pass

        else:
            if coloredlogs:
                try:
                    # Check if coloredlogs is available
                    import coloredlogs

                    coloredlogs.install(
                        level=logging.INFO,
                        fmt=formatters['simple'],
                        reconfigure=True
                    )

                except ImportError:
                    logger = logging.getLogger()
                    logger.setLevel(default_level)

                    console_info = logging.StreamHandler()
                    console_info.setLevel(logging.INFO)
                    console_info.setFormatter(logging.Formatter(formatters['simple']))
                    console_info.addFilter(LoggerFilter(logging.INFO))
                    logger.addHandler(console_info)

                    console_debug = logging.StreamHandler()
                    console_debug.setLevel(logging.DEBUG)
                    console_debug.setFormatter(logging.Formatter(formatters['simple']))
                    console_debug.addFilter(LoggerFilter(logging.DEBUG))
                    logger.addHandler(console_debug)

                    console_warning = logging.StreamHandler()
                    console_warning.setLevel(logging.WARNING)
                    console_warning.setFormatter(logging.Formatter(formatters['simple']))
                    console_warning.addFilter(LoggerFilter(logging.WARNING))
                    logger.addHandler(console_warning)

                    console_critical = logging.StreamHandler()
                    console_critical.setLevel(logging.CRITICAL)
                    console_critical.setFormatter(logging.Formatter(formatters['extended2']))
                    console_critical.addFilter(LoggerFilter(logging.CRITICAL))
                    logger.addHandler(console_critical)

                    console_error = logging.StreamHandler()
                    console_error.setLevel(logging.ERROR)
                    console_error.setFormatter(logging.Formatter(formatters['extended2']))
                    console_error.addFilter(LoggerFilter(logging.ERROR))
                    logger.addHandler(console_error)

                    if logging_file:
                        file_info = logging.handlers.RotatingFileHandler(
                            filename=logging_file,
                            maxBytes=10485760,
                            backupCount=20,
                            encoding='utf8'
                        )
                        file_info.setLevel(logging.INFO)
                        file_info.setFormatter(logging.Formatter(formatters['file_extended']))
                        logger.addHandler(file_info)

            else:
                logger = logging.getLogger()
                logger.setLevel(default_level)

                console_info = logging.StreamHandler()
                console_info.setLevel(logging.INFO)
                console_info.setFormatter(logging.Formatter(formatters['simple']))
                console_info.addFilter(LoggerFilter(logging.INFO))
                logger.addHandler(console_info)

                console_debug = logging.StreamHandler()
                console_debug.setLevel(logging.DEBUG)
                console_debug.setFormatter(logging.Formatter(formatters['simple']))
                console_debug.addFilter(LoggerFilter(logging.DEBUG))
                logger.addHandler(console_debug)

                console_warning = logging.StreamHandler()
                console_warning.setLevel(logging.WARNING)
                console_warning.setFormatter(logging.Formatter(formatters['simple']))
                console_warning.addFilter(LoggerFilter(logging.WARNING))
                logger.addHandler(console_warning)

                console_critical = logging.StreamHandler()
                console_critical.setLevel(logging.CRITICAL)
                console_critical.setFormatter(logging.Formatter(formatters['extended2']))
                console_critical.addFilter(LoggerFilter(logging.CRITICAL))
                logger.addHandler(console_critical)

                console_error = logging.StreamHandler()
                console_error.setLevel(logging.ERROR)
                console_error.setFormatter(logging.Formatter(formatters['extended2']))
                console_error.addFilter(LoggerFilter(logging.ERROR))
                logger.addHandler(console_error)

                if logging_file:
                    file_info = logging.handlers.RotatingFileHandler(
                        filename=logging_file,
                        maxBytes=10485760,
                        backupCount=20,
                        encoding='utf8'
                    )
                    file_info.setLevel(logging.INFO)
                    file_info.setFormatter(logging.Formatter(formatters['file_extended']))
                    logger.addHandler(file_info)

    else:
        from dcase_util.containers import DictContainer
        parameters = DictContainer(parameters)
        logging.config.dictConfig(parameters.get('parameters'))
        if (parameters.get('colored', False) and
           'console' in parameters.get_path('parameters.handlers')):

            try:
                # Check if coloredlogs is available
                import coloredlogs
                coloredlogs.install(
                    level=parameters.get_path('parameters.handlers.console.level'),
                    fmt=parameters.get_path('parameters.formatters')[
                        parameters.get_path('parameters.handlers.console.formatter')
                    ].get('format')
                )
            except ImportError:
                pass

    # Function to handle uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


class DisableLogger(object):
    def __enter__(self):
        logging.disable(logging.CRITICAL)
        return self

    def __exit__(self, *args):
        logging.disable(logging.NOTSET)

