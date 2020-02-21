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
    ProcessingChain.processor_exists
    ProcessingChain.processor_class_reference
    ProcessingChain.processor_class
    ProcessingChain.chain_item_exists
    ProcessingChain.chain_item
    ProcessingChain.call_method

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

AudioWritingProcessor
---------------------

*dcase_util.processors.AudioWritingProcessor*

.. autosummary::
    :toctree: generated/

    AudioWritingProcessor
    AudioWritingProcessor.process

MonoAudioWritingProcessor
-------------------------

*dcase_util.processors.MonoAudioWritingProcessor*

.. autosummary::
    :toctree: generated/

    MonoAudioWritingProcessor
    MonoAudioWritingProcessor.process

Data
::::

AggregationProcessor
--------------------

*dcase_util.processors.AggregationProcessor*

.. autosummary::
    :toctree: generated/

    AggregationProcessor
    AggregationProcessor.process

RepositoryAggregationProcessor
------------------------------

*dcase_util.processors.RepositoryAggregationProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryAggregationProcessor
    RepositoryAggregationProcessor.process

SequencingProcessor
-------------------

*dcase_util.processors.SequencingProcessor*

.. autosummary::
    :toctree: generated/

    SequencingProcessor
    SequencingProcessor.process

RepositorySequencingProcessor
-----------------------------

*dcase_util.processors.RepositorySequencingProcessor*

.. autosummary::
    :toctree: generated/

    RepositorySequencingProcessor
    RepositorySequencingProcessor.process

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

RepositoryMaskingProcessor
--------------------------

*dcase_util.processors.RepositoryMaskingProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryMaskingProcessor
    RepositoryMaskingProcessor.process

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

OneHotLabelEncodingProcessor
----------------------------

*dcase_util.processors.OneHotLabelEncodingProcessor*

.. autosummary::
    :toctree: generated/

    OneHotLabelEncodingProcessor
    OneHotLabelEncodingProcessor.process

DataShapingProcessor
--------------------

*dcase_util.processors.DataShapingProcessor*

.. autosummary::
    :toctree: generated/

    DataShapingProcessor
    DataShapingProcessor.process

RepositoryToMatrixProcessor
---------------------------

*dcase_util.processors.RepositoryToMatrixProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryToMatrixProcessor
    RepositoryToMatrixProcessor.process

Features
::::::::

FeatureReadingProcessor
-----------------------

*dcase_util.processors.FeatureReadingProcessor*

.. autosummary::
    :toctree: generated/

    FeatureReadingProcessor
    FeatureReadingProcessor.process

FeatureWritingProcessor
-----------------------

*dcase_util.processors.FeatureWritingProcessor*

.. autosummary::
    :toctree: generated/

    FeatureWritingProcessor
    FeatureWritingProcessor.process

RepositoryFeatureReadingProcessor
---------------------------------

*dcase_util.processors.RepositoryFeatureReadingProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryFeatureReadingProcessor
    RepositoryFeatureReadingProcessor.process

RepositoryFeatureWritingProcessor
---------------------------------

*dcase_util.processors.RepositoryFeatureWritingProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryFeatureWritingProcessor
    RepositoryFeatureWritingProcessor.process

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

RepositoryFeatureExtractorProcessor
-----------------------------------

*dcase_util.processors.RepositoryFeatureExtractorProcessor*

.. autosummary::
    :toctree: generated/

    RepositoryFeatureExtractorProcessor
    RepositoryFeatureExtractorProcessor.process

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

OpenL3ExtractorProcessor
------------------------

*dcase_util.processors.OpenL3ExtractorProcessor*

.. autosummary::
    :toctree: generated/

    OpenL3ExtractorProcessor
    OpenL3ExtractorProcessor.process

EdgeL3ExtractorProcessor
------------------------

*dcase_util.processors.EdgeL3ExtractorProcessor*

.. autosummary::
    :toctree: generated/

    EdgeL3ExtractorProcessor
    EdgeL3ExtractorProcessor.process

Metadata
::::::::

MetadataReadingProcessor
------------------------

*dcase_util.processors.MetadataReadingProcessor*

.. autosummary::
    :toctree: generated/

    MetadataReadingProcessor
    MetadataReadingProcessor.process

Base object
:::::::::::

Processor
---------

*dcase_util.processors.Processor*

.. autosummary::
    :toctree: generated/

    Processor
    Processor.process
    Processor.get_processing_chain_item

"""

from .processing_chain import *
from .processor import *
from .data import *
from .encoders import *
from .metadata import *
from .audio import *
from .features import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
