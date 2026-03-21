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
from . import tfkeras

__version__ = '0.2.11'


def check_installation():
    """Utility function to check package installation.
    """

    import os
    import platform
    import subprocess
    import sys
    from importlib import metadata as importlib_metadata

    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name

    def _parse_requirements(requirement_lines):
        parsed_requirements = []
        for requirement_line in requirement_lines:
            line = requirement_line.strip()
            if not line or line.startswith('#'):
                continue

            requirement = Requirement(line)
            if requirement.marker is None or requirement.marker.evaluate():
                parsed_requirements.append(requirement)

        return parsed_requirements

    def _requirements_from_file(filename):
        if filename and os.path.isfile(filename):
            with open(filename) as file_handle:
                return _parse_requirements(file_handle.readlines())
        return []

    def _requirement_spec(requirement):
        if requirement.specifier:
            return str(requirement.specifier)
        return '-'

    def _installed_status(requirement):
        try:
            installed_version = importlib_metadata.version(requirement.name)
        except importlib_metadata.PackageNotFoundError:
            return 'N/A', 'MISSING'

        if requirement.specifier and not requirement.specifier.contains(installed_version, prereleases=True):
            return installed_version, 'CHECK'

        return installed_version, 'OK'

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

    package_distribution = None
    core_requirements = []
    requirements_filename = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'requirements.txt')
    )

    try:
        package_distribution = importlib_metadata.distribution('dcase_util')
    except importlib_metadata.PackageNotFoundError:
        package_distribution = None

    if package_distribution is not None:
        core_requirements = _parse_requirements(package_distribution.requires or [])
        package_requirements_filename = os.path.abspath(str(package_distribution.locate_file('requirements.txt')))
        if os.path.isfile(package_requirements_filename):
            requirements_filename = package_requirements_filename

    if not core_requirements:
        core_requirements = _requirements_from_file(requirements_filename)

    all_requirements = _requirements_from_file(requirements_filename)
    if not all_requirements:
        all_requirements = list(core_requirements)

    processed = set()

    log.line('Core requirements')
    log.row('Package', 'Required', 'Installed', 'Status', widths=[25, 15, 15, 15])
    log.row_sep()
    for requirement in core_requirements:
        requirement_name = canonicalize_name(requirement.name)
        if requirement_name not in processed:
            installed, status = _installed_status(requirement)
            log.row(
                requirement.name,
                _requirement_spec(requirement),
                installed,
                status
            )
            processed.add(requirement_name)
    log.line()

    log.line('Extra requirements')
    log.row('Package', 'Required', 'Installed', 'Status', widths=[25, 15, 15, 15])
    log.row_sep()
    for requirement in all_requirements:
        requirement_name = canonicalize_name(requirement.name)
        if requirement_name not in processed:
            installed, status = _installed_status(requirement)
            log.row(
                requirement.name,
                _requirement_spec(requirement),
                installed,
                status
            )
            processed.add(requirement_name)
    log.line()

    # Get system level requirements
    log.line('System')
    try:
        ffmpeg_info = subprocess.check_output(
            ['ffmpeg', '-version'],
            stderr=subprocess.STDOUT
        ).decode('utf-8')
    except (subprocess.CalledProcessError, OSError) as error:
        ffmpeg_info = str(error)

    log.data(field='FFMPEG', value=ffmpeg_info)
