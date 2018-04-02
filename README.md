DCASE Utilities
===============

A collection of utilities for Detection and Classification of Acoustic Scenes and Events

[![Build Status](https://travis-ci.org/DCASE-REPO/dcase_util.svg?branch=master)](https://travis-ci.org/DCASE-REPO/dcase_util)
[![Coverage Status](https://coveralls.io/repos/github/DCASE-REPO/dcase_util/badge.svg?branch=master)](https://coveralls.io/github/DCASE-REPO/dcase_util?branch=master)
[![Code Health](https://landscape.io/github/DCASE-REPO/dcase_util/master/landscape.svg?style=flat)](https://landscape.io/github/DCASE-REPO/dcase_util/master)
[![PyPI](https://img.shields.io/pypi/v/dcase_util.svg)](https://pypi.python.org/pypi/dcase_util)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

This collection of utilities is for Detection and Classification of Acoustic Scenes
and Events (DCASE). These utilities were originally created for the DCASE challenge baseline systems
([2016](https://github.com/TUT-ARG/DCASE2016-baseline-system-python) &
[2017](https://github.com/TUT-ARG/DCASE2017-baseline-system)) and are bundled into a standalone library
to allow their re-usage in other research projects.

The main goal of the utilities is to streamline the research code, make it more readable, and easier to maintain.
Most of the implemented utilities are related to audio datasets: handling meta data and various forms of other
structured data, and provide standardized usage API to audio datasets from various sources.

Documentation
=============

See https://dcase-repo.github.io/dcase_util/ for detailed instruction, manuals and tutorials.

Installation instructions
=========================

The latest stable release is available on PyPI, and you can install with pip:
`pip install dcase_util` 

Changelog
=========

#### master

* Add new processors `FeatureReadingProcessor`, `DataShapingProcessor`, `RepositoryAggregationProcessor`, `RepositorySequencingProcessor`, and  `RepositoryToMatrixProcessor`
* Add extract method to `SpectralFeatureExtractor`
* Add automatic conversion of numeric fields when loading CSV data to `ListDictContainer`
* Add filter and get_field_unique methods to `ListDictContainer`
* Add MP4 to valid audio formats for `AudioContainer`
* Add general path modification method (`Path.modify`)
* Add Keras profile `cuda0_fast`
* Add Keras utility to create optimizer instance (`create_optimizer`)
* Add `DCASE2018_Task5_DevelopmentSet` and `DCASE2013_Scenes_EvaluationSet` datasets
* Add `DataMatrix4DContainer`
* Add `plot` method to `DataMatrix3DContainer`
* Add support for a new annotation format for tags [filename][tab][tags] in `MetaDataContainer`
* Add zero padding to `Sequencer`
* Add header field override in `load` method of `MetaDataContainer` 
* Add support for new compressed audio formats (OGG, MP3) in `AudioContainer`
* Add `segments` method in `AudioContainer` to split signal into non-overlapping segments with optionally skipped regions
* Add `pad` method in `AudioContainer` to pad signal into given length
* Add `compress` method in `PackageMixin`
* Add `Package` class to handle local compressed file packages
* Add `change_axis` method to `DataMatrix2DContainer`, `DataMatrix3DContainer`, and `DataMatrix4DContainer`
* Add `KerasDataSequence` class for data generation through processing chain
* Add support for data and meta processing chains to `DCASEAppParameterContainer`
* Add `many_hot` method in `DecisionEncoder`  
* Update `TUTRareSoundEvents_2017_DevelopmentSet` and `TUTRareSoundEvents_2017_EvaluationSet` datasets
* Update Keras utility `model_summary_string` to use by default standard method from Keras
* Update `FeatureRepository` API to be aligned with Container classes
* Update `Sequencer` API 
* Update `AppParameterContainer` to allow change of active set even after `process` method has been called
* Update mechanism to store meta information about chain item when data is processed using processing chain   
* Fix `save` method in `MetaDataContainer` when saving with tags in CSV format
* Fix many methods to give more appropriate error messages

#### 0.1.8 / 2018-01-29

* Add new formats for `MetaDataContainer` (cpickle, CSV)
* Add forced file formats when reading and saving containers
* Add Keras setup function
* Add frame splitting method into `AudioContainer`
* Fix unicode string support when printing container information
* Fix data contamination through data references while manipulating data
* Some minor bug fixes

#### 0.1.7 / 2017-11-22

* Add intersection method for `MetaDataContainer `
* Update dataset class API (e.g. copy returned metadata prevent accidental manipulation, uniform method names)
* Fix data sequencing when overlapping sequencing is used.
* Fix datasets `CHiMEHome_DomesticAudioTag_DevelopmentSet`, `TUTAcousticScenes_2017_EvaluationSet`, and `TUTSoundEvents_2017_EvaluationSet`


#### 0.1.6 / 2017-11-14

* Add `CHiMEHome_DomesticAudioTag_EvaluationSet` dataset
* Update example audio to be 16-bit audio file in wav-format instead of FLAC used earlier
* Update `ProbabilityContainer` API to be more compatible with `MetaDataContainer`
* Update `MetaDataItem` to be compatible with field naming used previously in DCASE baseline systems
* Update ui utilities
* Fix audio reading when target sampling rate is not set
* Some minor bug fixes

#### 0.1.5 / 2017-11-10

* Fixing PYPI package

#### 0.1.4 / 2017-11-10

* Release PYPI package

#### 0.1.0 / 2017-11-09

* Initial public release

License
=======

Code released under the [MIT license](https://github.com/DCASE-REPO/dcase_util/tree/master/LICENSE).
