# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools
=====

Utility classes for specific purpose, mainly for processing DCASE challenge submissions for publishing.

SubmissionChecker
^^^^^^^^^^^^^^^^^

*dcase_util.tools.SubmissionChecker*

SubmissionChecker class can be used to check DCASE challenge submission meta yaml files.

.. autosummary::
    :toctree: generated/

    SubmissionChecker
    SubmissionChecker.process
    SubmissionChecker.parameter_file
    SubmissionChecker.system_output_file
    SubmissionChecker.main_structure
    SubmissionChecker.submission_info
    SubmissionChecker.system_meta
    SubmissionChecker.system_description
    SubmissionChecker.system_output

BibtexProcessor
^^^^^^^^^^^^^^^

*dcase_util.tools.BibtexProcessor*

This class provides tools to form bibtex entries for the DCASE challenge submissions.

.. autosummary::
    :toctree: generated/

    BibtexProcessor
    BibtexProcessor.key
    BibtexProcessor.authors
    BibtexProcessor.authors_fancy
    BibtexProcessor.affiliation_str
    BibtexProcessor.affiliation_list
    BibtexProcessor.affiliation_list_fancy
    BibtexProcessor.submissions_fancy
    BibtexProcessor.title
    BibtexProcessor.abstract

"""

from .bibtex import *
from .submission import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
