#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Top-level"""

# Import all sub-modules
from . import containers
from . import containers as c
from . import datasets
from . import decorators
from . import files
from . import features
from . import ui
from . import utils
from . import data
from . import processors
from . import tools
from . import keras

__version__ = '0.2.11'


def check_installation():
    """Utility function to check package installation.
    """

    import pkg_resources
    import os
    import sys
    import platform
    import subprocess

    log = ui.FancyPrinter()

    # Get system information
    log.line('System information')
    log.data(field='System', value=platform.system())
    log.data(field='Release', value=platform.release())
    log.data(field='Version', value=platform.version())
    log.data(field='Processor', value=platform.processor())
    log.line()

    # Get Python installation information
    log.line('Python information')
    log.data(field='Version', value=sys.version)
    log.data(field='Compiler', value=platform.python_compiler())
    log.data(field='Implementation', value=platform.python_implementation())
    log.line()

    # Get package information
    log.line('Package information')
    log.data(field='Name', value=__name__)
    log.data(field='Version', value=__version__)
    log.line()

    package = pkg_resources.require('dcase_util')[0]

    # Get core requirements
    core_requirements = package.requires()

    # Load requirements.txt
    requirements_filename = os.path.join(package.location, 'requirements.txt')
    with open(requirements_filename) as fp:
        requirements_file = fp.read()

    # Get all requirements
    all_requirements = []
    for r in pkg_resources.parse_requirements(requirements_file):
        if r.marker:
            raise ValueError("environment markers are not supported, in '%s'" % r)
        all_requirements.append(r)

    processed = []

    log.line('Core requirements')
    log.row('Package', 'Required', 'Installed', 'Status', widths=[25, 15, 15, 15])
    log.row_sep()
    for requirement in core_requirements:
        if requirement.key not in processed:
            log.row(
                requirement.key,
                ''.join(requirement.specs[0]),
                pkg_resources.get_distribution(requirement.key).version,
                'OK' if requirement.__contains__(pkg_resources.get_distribution(requirement.key)) else 'CHECK'
            )
            processed.append(requirement.key)
    log.line()

    log.line('Extra requirements')
    log.row('Package', 'Required', 'Installed', 'Status', widths=[25, 15, 15, 15])
    log.row_sep()
    for requirement in all_requirements:
        if requirement.key not in processed:
            log.row(
                requirement.key,
                ''.join(requirement.specs[0]),
                pkg_resources.get_distribution(requirement.key).version,
                'OK' if requirement.__contains__(pkg_resources.get_distribution(requirement.key)) else 'CHECK'
            )
            processed.append(requirement.key)
    log.line()

    # Get system level requirements
    log.line('System')
    ffmpeg_info = subprocess.check_output(['ffmpeg', '-version']).decode('utf-8')

    log.data(field='FFMPEG', value=ffmpeg_info)
