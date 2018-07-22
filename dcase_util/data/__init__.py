# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data
====

Classes for data handling

Buffers
:::::::

DataBuffer
----------

*dcase_util.data.DataBuffer*

Data buffering class, which can be used to store data and meta data associated to the item. Item data is accessed
through item key. When internal buffer is filled, oldest item is replaced.

.. autosummary::
    :toctree: generated/

    DataBuffer
    DataBuffer.set
    DataBuffer.get
    DataBuffer.clear
    DataBuffer.count
    DataBuffer.full
    DataBuffer.key_exists

Encoders
::::::::

BinaryMatrixEncoder
-------------------

*dcase_util.data.BinaryMatrixEncoder*

.. autosummary::
    :toctree: generated/

    BinaryMatrixEncoder
    BinaryMatrixEncoder.pad
    BinaryMatrixEncoder.plot

OneHotEncoder
-------------

*dcase_util.data.OneHotEncoder*

.. autosummary::
    :toctree: generated/

    OneHotEncoder
    OneHotEncoder.encode


ManyHotEncoder
--------------

*dcase_util.data.ManyHotEncoder*

.. autosummary::
    :toctree: generated/

    ManyHotEncoder
    ManyHotEncoder.encode

EventRollEncoder
----------------

*dcase_util.data.EventRollEncoder*

.. autosummary::
    :toctree: generated/

    EventRollEncoder
    EventRollEncoder.encode

LabelMatrixEncoder
------------------

*dcase_util.data.LabelMatrixEncoder*

.. autosummary::
    :toctree: generated/

    LabelMatrixEncoder

OneHotLabelEncoder
------------------

*dcase_util.data.OneHotLabelEncoder*

.. autosummary::
    :toctree: generated/

    OneHotLabelEncoder
    OneHotLabelEncoder.encode

Data manipulators
:::::::::::::::::

Normalizer
----------

*dcase_util.data.Normalizer*

.. autosummary::
    :toctree: generated/

    Normalizer
    Normalizer.log
    Normalizer.show
    Normalizer.load
    Normalizer.save
    Normalizer.mean
    Normalizer.std
    Normalizer.reset
    Normalizer.accumulate
    Normalizer.finalize
    Normalizer.normalize

RepositoryNormalizer
--------------------

*dcase_util.data.RepositoryNormalizer*

.. autosummary::
    :toctree: generated/

    RepositoryNormalizer
    RepositoryNormalizer.load
    RepositoryNormalizer.normalize

Aggregator
----------

*dcase_util.data.Aggregator*

Data aggregator can be used to process data matrix in a processing windows.
This processing stage can be used to collapse data within certain window lengths by
calculating mean and std of them, or flatten the matrix into single vector.

Supported processing methods:

- ``flatten``
- ``mean``
- ``std``
- ``cov``
- ``kurtosis``
- ``skew``

The processing methods can combined.

Usage examples:

.. code-block:: python
    :linenos:

    data_aggregator = dcase_util.data.Aggregator(
        recipe=['mean', 'std'],
        win_length_frames=10,
        hop_length_frames=1,
    )

    data_stacker = dcase_util.data.Stacker(recipe='mfcc')
    data_repository = dcase_util.utils.Example.feature_repository()
    data_matrix = data_stacker.stack(data_repository)
    data_matrix = data_aggregator.aggregate(data_matrix)

.. autosummary::
    :toctree: generated/

    Aggregator
    Aggregator.log
    Aggregator.show
    Aggregator.load
    Aggregator.save
    Aggregator.aggregate

Sequencer
----------

*dcase_util.data.Sequencer*

Sequencer class processes data matrices into sequences (images). Sequences can overlap, and sequencing grid can be
altered between calls (shifted).

.. autosummary::
    :toctree: generated/

    Sequencer
    Sequencer.log
    Sequencer.show
    Sequencer.load
    Sequencer.save
    Sequencer.sequence
    Sequencer.increase_shifting

Stacker
-------

*dcase_util.data.Stacker*

Data stacking class. Class takes vector recipe and DataRepository, and creates appropriate data matrix.

**Vector recipe**

With a recipe one can either select full matrix, only part of with start and end index, or select individual rows
from it.

Example recipe:

.. code-block:: python
    :linenos:

    [
     {
        'method': 'mfcc',
     },
     {
        'method': 'mfcc_delta'
        'vector-index: {
            'channel': 0,
            'start': 1,
            'end': 17,
            'full': False,
            'selection': False,
        }
      },
     {
        'method': 'mfcc_acceleration',
        'vector-index: {
            'channel': 0,
            'full': False,
            'selection': True,
            'vector': [2, 4, 6]
        }
     }
    ]

See  :py:meth:`dcase_util.utils.VectorRecipeParser` how recipe string can be conveniently used to generate
above data structure.

.. autosummary::
    :toctree: generated/

    Stacker
    Stacker.log
    Stacker.show
    Stacker.load
    Stacker.save
    Stacker.stack


Selector
--------

*dcase_util.data.Selector*

Data selecting class.

.. autosummary::
    :toctree: generated/

    Selector
    Selector.log
    Selector.show
    Selector.load
    Selector.save
    Selector.select

Masker
------

*dcase_util.data.Masker*

Data masking class.

.. autosummary::
    :toctree: generated/

    Masker
    Masker.log
    Masker.show
    Masker.load
    Masker.save
    Masker.mask

Probabilities
:::::::::::::

ProbabilityEncoder
------------------

*dcase_util.data.ProbabilityEncoder*

.. autosummary::
    :toctree: generated/

    ProbabilityEncoder
    ProbabilityEncoder.log
    ProbabilityEncoder.show
    ProbabilityEncoder.load
    ProbabilityEncoder.save
    ProbabilityEncoder.collapse_probabilities
    ProbabilityEncoder.collapse_probabilities_windowed
    ProbabilityEncoder.binarization

Decisions
:::::::::

DecisionEncoder
---------------

*dcase_util.data.DecisionEncoder*

.. autosummary::
    :toctree: generated/

    DecisionEncoder
    DecisionEncoder.log
    DecisionEncoder.show
    DecisionEncoder.load
    DecisionEncoder.save
    DecisionEncoder.majority_vote
    DecisionEncoder.many_hot
    DecisionEncoder.find_contiguous_regions
    DecisionEncoder.process_activity

"""

from .encoders import *
from .buffers import *
from .manipulators import *
from .probabilities import *
from .decisions import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
