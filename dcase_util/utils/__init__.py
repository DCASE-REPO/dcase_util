# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utils
=====

Utility functions and classes.

General functions
:::::::::::::::::

*dcase_util.utils.* *

.. autosummary::
    :toctree: generated/

    get_audio_info
    get_class_inheritors
    get_byte_string
    check_pkg_resources
    is_int
    is_float
    is_jupyter

SuppressStdoutAndStderr
-----------------------

*dcase_util.utils.SuppressStdoutAndStderr*

.. autosummary::
    :toctree: generated/

    SuppressStdoutAndStderr

VectorRecipeParser
------------------

*dcase_util.utils.VectorRecipeParser*

.. autosummary::
    :toctree: generated/

    VectorRecipeParser

Files
:::::

*dcase_util.utils.* *

.. autosummary::
    :toctree: generated/

    argument_file_exists
    filelist_exists
    posix_path

Path
----

*dcase_util.utils.Path*

.. autosummary::
    :toctree: generated/

    Path
    Path.posix
    Path.posix_to_nt
    Path.file_list
    Path.exists
    Path.file_count
    Path.size_bytes
    Path.size_string
    Path.makedirs
    Path.create


ApplicationPaths
----------------

*dcase_util.utils.ApplicationPaths*

.. autosummary::
    :toctree: generated/

    ApplicationPaths
    ApplicationPaths.generate
    ApplicationPaths.directory_name
    ApplicationPaths.save_parameters_to_path
    ApplicationPaths.construct_path

FileFormat
----------

*dcase_util.utils.FileFormat*

.. autosummary::
    :toctree: generated/

    FileFormat
    FileFormat.detect
    FileFormat.detect_based_on_filename
    FileFormat.detect_based_on_content
    FileFormat.validate_label

Hash
::::

.. autosummary::
    :toctree: generated/

    get_parameter_hash
    get_file_hash

Logging
:::::::

.. autosummary::
    :toctree: generated/

    setup_logging

DisableLogger
-------------

*dcase_util.utils.DisableLogger*

.. autosummary::
    :toctree: generated/

    DisableLogger

Math
::::

*dcase_util.utils.SimpleMathStringEvaluator*

SimpleMathStringEvaluator
-------------------------

.. autosummary::
    :toctree: generated/

    SimpleMathStringEvaluator
    SimpleMathStringEvaluator.eval

Timer
:::::

*dcase_util.utils.Timer*

.. autosummary::
    :toctree: generated/

    Timer
    Timer.start
    Timer.stop
    Timer.elapsed
    Timer.get_string

Validators
::::::::::


FieldValidator
--------------

*dcase_util.utils.FieldValidator*

.. autosummary::
    :toctree: generated/

    FieldValidator
    FieldValidator.process
    FieldValidator.is_empty
    FieldValidator.is_number
    FieldValidator.is_audiofile
    FieldValidator.is_list
    FieldValidator.is_alpha

Examples
::::::::

*dcase_util.utils.Example*

Some example data for easy testing and tutoring.

.. autosummary::
    :toctree: generated/

    Example
    Example.audio_filename
    Example.acoustic_scene_audio_filename
    Example.audio_filename_mp3
    Example.acoustic_scene_audio_filename_mp3
    Example.audio_container
    Example.event_metadata_container
    Example.scene_metadata_container
    Example.tag_metadata_container
    Example.feature_container
    Example.feature_repository

"""

from .utils import *
from .timer import *
from .math import *
from .hash import *
from .logging import *
from .validators import *
from .files import *
from .examples import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
