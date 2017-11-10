.. figure:: _images/dcase_util.png

*Utilities for Detection and Classification of Acoustic Scenes*

This document describes the collection of utilities created for Detection and Classification of Acoustic Scenes
and Events (DCASE). These utilities were originally created for the DCASE challenge baseline systems
(`2016 <https://github.com/TUT-ARG/DCASE2016-baseline-system-python>`_ &
`2017 <https://github.com/TUT-ARG/DCASE2017-baseline-system>`_) and are bundled into a standalone library
to allow their re-usage in other research projects.

The main goal of the utilities is to streamline the research code, make it more readable, and easier to maintain.
Most of the implemented utilities are related to audio datasets: handling meta data and various forms of other
structured data, and provide standardized usage API to audio datasets from various sources.

Initial version written by Toni Heittola from
`Audio Research Group, Tampere University of Technology <http://arg.cs.tut.fi/>`_, you can contact him
via `personal website <http://www.cs.tut.fi/~heittolt/>`_ or `github <https://github.com/toni-heittola>`_.

Getting started
---------------

Easiest to get started with the library is to use pip to install the latest stable release::

    pip install dcase_util


Alternative installation methods can be found in the :ref:`installation instructions <installation>`.

See :ref:`tutorials <tutorial_introduction>` how to use `dcase_util`.

Troubleshooting
---------------

If you have questions about how to use dcase_util, please consult the discussion forum. For bug reports and other, more technical issues, consult the github issues.

Contents
========

.. toctree::
    :name: maintoc
    :maxdepth: 1

    installation
    library

.. toctree::
    :caption: Tutorials
    :name: tutorialtoc
    :maxdepth: 1

    tutorial_introduction
    tutorial_containers
    tutorial_audio
    tutorial_features
    tutorial_data
    tutorial_metadata
    tutorial_datasets
    tutorial_processing_chain
    tutorial_applications

.. toctree::
    :caption: Utilities
    :name: utiltoc
    :maxdepth: 1

    containers
    data
    datasets
    decorators
    features
    files
    keras
    processors
    ui
    utils

.. toctree::
    :caption: Tools
    :name: toolstoc
    :maxdepth: 1

    tools

.. toctree::
    :caption: Reference
    :maxdepth: 1

    changelog
    glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
