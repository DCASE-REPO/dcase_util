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

#### 0.1.8 / 2018-01-29

* Add new formats for MetaDataContainer (cpickle, csv)
* Fix unicode string support when printing container information
* Fixing data contamination through data references while manipulating data
* Add forced file formats when reading and saving containers
* Add keras setup function
* Add frame splitting method into AudioContainer
* Some minor bug fixes.

#### 0.1.7 / 2017-11-22

* Fix data sequencing when overlapping sequencing is used. 
* Dataset class API modifications (e.g. copy returned metadata prevent accidental manipulation, uniform method names)
* Fix datasets CHiMEHome_DomesticAudioTag_DevelopmentSet, TUTAcousticScenes_2017_EvaluationSet, and TUTSoundEvents_2017_EvaluationSet
* Add intersection method for MetaDataContainer 

#### 0.1.6 / 2017-11-14

* Fixing audio reading when target sampling rate is not set
* Some minor tweaks to ui utilities. 
* Example audio is now 16-bit audio file in wav-format instead of FLAC used earlier.
* ProbabilityContainer API is more compatible with MetaDataContainer now.
* MetaDataItem is now compatible with field naming used previously in DCASE baselines
* Add CHiMEHome_DomesticAudioTag_EvaluationSet dataset.
* Some minor bug fixes.

#### 0.1.5 / 2017-11-10

* Fixing PYPI package

#### 0.1.4 / 2017-11-10

* Release PYPI package

#### 0.1.0 / 2017-11-09

* Initial public release

License
=======

Code released under the [MIT license](https://github.com/DCASE-REPO/dcase_util/tree/master/LICENSE).
