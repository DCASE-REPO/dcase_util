# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tools
=====

Utility classes for specific purpose, mainly for processing DCASE challenge submissions for publishing.

DatasetPacker
^^^^^^^^^^^^^

*dcase_util.tools.DatasetPacker*

DatasetPacker class can be used to create DCASE styled dataset packages where different data types delivered with
separate packages. Large data packages are split into multiple smalled ones to ease downloading them over net.

.. autosummary::
    :toctree: generated/

    DatasetPacker
    DatasetPacker.pack
    DatasetPacker.convert_markdown

SubmissionChecker
^^^^^^^^^^^^^^^^^

*dcase_util.tools.SubmissionChecker*

SubmissionChecker class can be used to check DCASE challenge submission meta yaml files.

.. autosummary::
    :toctree: generated/

    SubmissionChecker
    SubmissionChecker.process

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
from .datasets import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
