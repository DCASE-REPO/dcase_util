.. _changelog:

Release notes
=============

v0.1.7
------

- Fix data sequencing when overlapping sequencing is used.
- Dataset class API modifications (e.g. copy returned metadata prevent accidental manipulation, uniform method names)
- Fix datasets CHiMEHome_DomesticAudioTag_DevelopmentSet, TUTAcousticScenes_2017_EvaluationSet, and TUTSoundEvents_2017_EvaluationSet
- Add intersection method for MetaDataContainer

v0.1.6
------

- Fixing audio reading when target sampling rate is not set
- Some minor tweaks to ui utilities.
- Example audio is now 16-bit audio file in wav-format instead of FLAC used earlier.
- ProbabilityContainer API is more compatible with MetaDataContainer now.
- MetaDataItem is now compatible with field naming used previously in DCASE baselines
- Add CHiMEHome_DomesticAudioTag_EvaluationSet dataset.
- Some minor bug fixes.

v0.1.5
------

- Fixing PYPI package.

v0.1.4
------

- Release first PYPI package.

v0.1.0
------

- Initial public release.