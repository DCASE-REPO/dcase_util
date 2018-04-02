.. _changelog:

Release notes
=============

v0.1.8
------

* Add new formats for `MetaDataContainer` (cpickle, CSV)
* Add forced file formats when reading and saving containers
* Add Keras setup function
* Add frame splitting method into `AudioContainer`
* Fix unicode string support when printing container information
* Fix data contamination through data references while manipulating data
* Some minor bug fixes

v0.1.7
------

* Add intersection method for `MetaDataContainer `
* Update dataset class API (e.g. copy returned metadata prevent accidental manipulation, uniform method names)
* Fix data sequencing when overlapping sequencing is used.
* Fix datasets `CHiMEHome_DomesticAudioTag_DevelopmentSet`, `TUTAcousticScenes_2017_EvaluationSet`, and `TUTSoundEvents_2017_EvaluationSet`

v0.1.6
------

* Add `CHiMEHome_DomesticAudioTag_EvaluationSet` dataset
* Update example audio to be 16-bit audio file in wav-format instead of FLAC used earlier
* Update `ProbabilityContainer` API to be more compatible with `MetaDataContainer`
* Update `MetaDataItem` to be compatible with field naming used previously in DCASE baseline systems
* Update ui utilities
* Fix audio reading when target sampling rate is not set
* Some minor bug fixes

v0.1.5
------

* Fixing PYPI package.

v0.1.4
------

* Release first PYPI package.

v0.1.0
------

* Initial public release.