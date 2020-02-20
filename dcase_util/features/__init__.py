# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Features
========

Classes for feature extraction.

FeatureExtractor
----------------

*dcase_util.features.FeatureExtractor*

.. autosummary::
    :toctree: generated/

    FeatureExtractor

SpectralFeatureExtractor
------------------------

*dcase_util.features.SpectralFeatureExtractor*

.. autosummary::
    :toctree: generated/

    SpectralFeatureExtractor
    SpectralFeatureExtractor.extract
    SpectralFeatureExtractor.get_window_function
    SpectralFeatureExtractor.get_spectrogram

MelExtractor
------------

*dcase_util.features.MelExtractor*

.. autosummary::
    :toctree: generated/

    MelExtractor
    MelExtractor.extract

MfccStaticExtractor
-------------------

*dcase_util.features.MfccStaticExtractor*

.. autosummary::
    :toctree: generated/

    MfccStaticExtractor
    MfccStaticExtractor.extract

MfccDeltaExtractor
------------------

*dcase_util.features.MfccDeltaExtractor*

.. autosummary::
    :toctree: generated/

    MfccDeltaExtractor
    MfccDeltaExtractor.extract

MfccAccelerationExtractor
-------------------------

*dcase_util.features.MfccAccelerationExtractor*

.. autosummary::
    :toctree: generated/

    MfccAccelerationExtractor
    MfccAccelerationExtractor.extract

ZeroCrossingRateExtractor
-------------------------

*dcase_util.features.ZeroCrossingRateExtractor*

.. autosummary::
    :toctree: generated/

    ZeroCrossingRateExtractor
    ZeroCrossingRateExtractor.extract

RMSEnergyExtractor
------------------

*dcase_util.features.RMSEnergyExtractor*

.. autosummary::
    :toctree: generated/

    RMSEnergyExtractor
    RMSEnergyExtractor.extract

SpectralCentroidExtractor
-------------------------

*dcase_util.features.SpectralCentroidExtractor*

.. autosummary::
    :toctree: generated/

    SpectralCentroidExtractor
    SpectralCentroidExtractor.extract


EmbeddingExtractor
------------------

*dcase_util.features.EmbeddingExtractor*

.. autosummary::
    :toctree: generated/

    EmbeddingExtractor

OpenL3Extractor
---------------

*dcase_util.features.OpenL3Extractor*

.. autosummary::
    :toctree: generated/

    OpenL3Extractor
    OpenL3Extractor.extract

EdgeL3Extractor
---------------

*dcase_util.features.EdgeL3Extractor*

.. autosummary::
    :toctree: generated/

    EdgeL3Extractor
    EdgeL3Extractor.extract

"""

from .features import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
