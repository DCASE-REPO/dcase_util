# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Processors
==========

Data processor classes.


Processing chain
::::::::::::::::

ProcessingChainItem
-------------------

*dcase_util.processors.ProcessingChainItem*

.. autosummary::
    :toctree: generated/

    ProcessingChainItem

ProcessingChain
---------------

*dcase_util.processors.ProcessingChain*

.. autosummary::
    :toctree: generated/

    ProcessingChain
    ProcessingChain.show_chain
    ProcessingChain.log_chain
    ProcessingChain.push_processor
    ProcessingChain.process
    ProcessingChain.call_method
    ProcessingChain.processor_exists
    ProcessingChain.processor_class_reference
    ProcessingChain.processor_class

Audio
:::::

AudioReadingProcessor
---------------------

*dcase_util.processors.AudioReadingProcessor*

.. autosummary::
    :toctree: generated/

    AudioReadingProcessor
    AudioReadingProcessor.process

MonoAudioReadingProcessor
-------------------------

*dcase_util.processors.MonoAudioReadingProcessor*

.. autosummary::
    :toctree: generated/

    MonoAudioReadingProcessor
    MonoAudioReadingProcessor.process

Data
::::

AggregationProcessor
--------------------

*dcase_util.processors.AggregationProcessor*

.. autosummary::
    :toctree: generated/

    AggregationProcessor
    AggregationProcessor.process

SequencingProcessor
-------------------

*dcase_util.processors.SequencingProcessor*

.. autosummary::
    :toctree: generated/

    SequencingProcessor
    SequencingProcessor.process


NormalizationProcessor
----------------------

*dcase_util.processors.NormalizationProcessor*

.. autosummary::
    :toctree: generated/

    NormalizationProcessor
    NormalizationProcessor.process


RepositoryNormalizationProcessor
--------------------------------

*dcase_util.processors.RepositoryNormalizationProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryNormalizationProcessor
    RepositoryNormalizationProcessor.process

StackingProcessor
-----------------

*dcase_util.processors.StackingProcessor*

.. autosummary::
    :toctree: generated/

    StackingProcessor
    StackingProcessor.process

OneHotEncodingProcessor
-----------------------

*dcase_util.processors.OneHotEncodingProcessor*

.. autosummary::
    :toctree: generated/

    OneHotEncodingProcessor
    OneHotEncodingProcessor.process

ManyHotEncodingProcessor
------------------------

*dcase_util.processors.ManyHotEncodingProcessor*

.. autosummary::
    :toctree: generated/

    ManyHotEncodingProcessor
    ManyHotEncodingProcessor.process

EventRollEncodingProcessor
--------------------------

*dcase_util.processors.EventRollEncodingProcessor*

.. autosummary::
    :toctree: generated/

    EventRollEncodingProcessor
    EventRollEncodingProcessor.process

Features
::::::::

RepositoryFeatureExtractorProcessor
-----------------------------------

*dcase_util.processors.RepositoryFeatureExtractorProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryFeatureExtractorProcessor
    RepositoryFeatureExtractorProcessor.process

FeatureExtractorProcessor
-------------------------

*dcase_util.processors.FeatureExtractorProcessor*

.. autosummary::
    :toctree: generated/

    FeatureExtractorProcessor
    FeatureExtractorProcessor.process

MelExtractorProcessor
---------------------

*dcase_util.processors.MelExtractorProcessor*

.. autosummary::
    :toctree: generated/

    MelExtractorProcessor
    MelExtractorProcessor.process

MfccStaticExtractorProcessor
----------------------------

*dcase_util.processors.MfccStaticExtractorProcessor*

.. autosummary::
    :toctree: generated/

    MfccStaticExtractorProcessor
    MfccStaticExtractorProcessor.process

MfccDeltaExtractorProcessor
---------------------------

*dcase_util.processors.MfccDeltaExtractorProcessor*

.. autosummary::
    :toctree: generated/

    MfccDeltaExtractorProcessor
    MfccDeltaExtractorProcessor.process

MfccAccelerationExtractorProcessor
----------------------------------

*dcase_util.processors.MfccAccelerationExtractorProcessor*

.. autosummary::
    :toctree: generated/

    MfccAccelerationExtractorProcessor
    MfccAccelerationExtractorProcessor.process

ZeroCrossingRateExtractorProcessor
----------------------------------

*dcase_util.processors.ZeroCrossingRateExtractorProcessor*

.. autosummary::
    :toctree: generated/

    ZeroCrossingRateExtractorProcessor
    ZeroCrossingRateExtractorProcessor.process

RMSEnergyExtractorProcessor
---------------------------

*dcase_util.processors.RMSEnergyExtractorProcessor*

.. autosummary::
    :toctree: generated/

    RMSEnergyExtractorProcessor
    RMSEnergyExtractorProcessor.process


SpectralCentroidExtractorProcessor
----------------------------------

*dcase_util.processors.SpectralCentroidExtractorProcessor*

.. autosummary::
    :toctree: generated/

    SpectralCentroidExtractorProcessor
    SpectralCentroidExtractorProcessor.process

Metadata
::::::::

MetadataReadingProcessor
------------------------

*dcase_util.processors.MetadataReadingProcessor*

.. autosummary::
    :toctree: generated/

    MetadataReadingProcessor
    MetadataReadingProcessor.process

Mixin
:::::

ProcessorMixin
--------------

*dcase_util.processors.ProcessorMixin*

.. autosummary::
    :toctree: generated/

    ProcessorMixin
    ProcessorMixin.process
    ProcessorMixin.get_processing_chain_item
    ProcessorMixin.push_processing_chain_item


"""

from .processing_chain import *
from .mixins import *
from .data import *
from .metadata import *
from .audio import *
from .features import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
