.. _changelog:

Release notes
=============

v0.2.9
------

**New features**

* Add ``TAUUrbanAcousticScenes_2019_EvaluationSet``, ``TAUUrbanAcousticScenes_2019_Mobile_EvaluationSet``, and ``TAUUrbanAcousticScenes_2019_Openset_EvaluationSet`` datasets.

v0.2.8
------

**New features**

* Add ``TAUUrbanAcousticScenes_2019_LeaderboardSet``, ``TAUUrbanAcousticScenes_2019_Mobile_LeaderboardSet``, and ``TAUUrbanAcousticScenes_2019_Openset_LeaderboardSet`` datasets.
* Add ``is_jupyter`` function to detect if code is running inside jupyter
* Add ``shorten`` method in ``Path`` to shorten long paths for visualization purpose
* Add ``FancyHTMLStringifier``, ``FancyHTMLPrinter`` classes for HTML output
* Add ``plot`` method in ``DataArrayContainer``
* Add ``plot`` method in ``Normalizer``

**Updates**

* Update YAML serialization to use ``yaml.FullLoader``
* ``formatted_value`` method in ``FancyStringifier`` to be static
* Refactor printing methods in containers to allow automatic output mode switching between HTML (Jypyter) and string (console)
* Update data printing mechanism for containers
* Update ``plot`` methods API to include ``figsize`` parameter
* Update default parameters in ``plot`` method in ``AudioContainer`` (color bar is hidden by default)
* Update error messages in ``AudioContainer`` to be more informative
* Update ``load`` method in ``MetaDataContainer`` to support additional row formats
* Update ``feature_extractor_list`` method to have option to return string or display (print to console or print as HTML output in Jupyter)
* Update ``dataset_list`` to use table layout and add option to return string or display (print to console or print as HTML output in Jupyter)
* Update ``to_string`` method in ``MetaDataContainer`` with option ``show_info`` to control what data is print
* Update API for methods ``show`` and ``log`` in ``Dataset`` to include ``show_meta`` parameter and ``mode`` parameter to control output format
* Update printing ``validation_files_balanced`` method in ``AcousticSceneDataset`` to support different output modes (print to console or print as HTML output in Jupyter)
* Update ``ProgressLoggerCallback`` to include ``show_timing`` parameter and ``notebook`` output type
* Update ``StasherCallback`` with ``to_string`` and ``show``
* Update printing inside ``setup_keras`` function
* Update ``model_summary_string`` function with new parameters (``show_parameters`` and ``display``)
* Update ``plot`` method in ``DataMatrix2DContainer`` with ``xlabel`` and ``ylabel`` parameters
* Update ``plot`` method in ``BinaryMatrix2DContainer`` with ``panel_title_position`` parameters
* Update usage of ``tqdm`` library in ``Dataset`` to allow locally progress bar disable/enable

**Bug fixes**

* Fix single channel audio plotting in ``AudioContainer``

v0.2.7
------

**Updates**

* Update ``TAUUrbanAcousticScenes_2019_Mobile_DevelopmentSet``, and ``TAUUrbanAcousticScenes_2019_Openset_DevelopmentSet`` datasets.

v0.2.6
------

**New features**

* Add ``TAUUrbanAcousticScenes_2019_DevelopmentSet``, ``TAUUrbanAcousticScenes_2019_Mobile_DevelopmentSet``, and ``TAUUrbanAcousticScenes_2019_Openset_DevelopmentSet`` datasets.
* Add ``OneHotEncoder`` and ``OneHotEncodingProcessor`` to allow unknown labels.
* Add automatic meta data check ups in datasets classes, and parameter to control it.
* Add ``AudioSequencingProcessor``
* Add ``feature_extractor_list`` to show all available feature extractors classes, and add description to all feature extraction classes.

**Updates**

* Update ``debug_packages`` method to allow better control which part of package_list is checked: remote or local.
* Update ``data_collector`` to have generic data axis handling.
* Update ``load`` method in ``ListDictContainer`` to skip empty rows in CSV files.
* Update ``save`` method in ``ListDictContainer`` for TXT and CSV to avoid extra empty lines under Windows.
* Update ``save`` method in ``MetaDataContainer`` for TXT and CSV to avoid extra empty lines under Windows.
* Update ``relative_to_absolute_path`` and ``absolute_to_relative_path`` to give more informative error messages.
* Update ``EventRollEncodingProcessor`` to support ``pad_length`` parameter.
* Update unit tests to be cross-platform compatible (Linux / Windows)
* Update ``SuppressStdoutAndStderr`` to be more robust
* Update ``MetaDataItem`` to keep filename field to be posix path when relative path is used.
* Update dtypes to be compatible with numpy v1.14
* Update ``setup_keras`` to warn when GPU was not found.
* Update ``model_summary_string`` to show activation function of the output layer.
* Update all processors, encoders, and manipulators have __call__ magic class method.

**Bug fixes**

* Fix delimiter detection in ``load`` method in ``MetaDataContainer``
* Fix ``MetaDataItem`` to better handle empty fields (onset, offset, and event_label).
* Fix how ``validation_split`` and ``validation_files_dataset`` method uses ``training_meta`` parameter.

v0.2.5
------

**New features**

* Add ``SoundDataset`` base class.
* Add ``feature_extractor_factory`` to get feature extractor class based on feature label.
* Add ``OneHotLabelEncoder`` label based encoder.
* Add ``OneHotLabelEncodingProcessor`` class.
* Add ``DBR_Dataset`` class.
* Add ``map_events`` method to ``MetaDataContainer`` to map multiple event labels into single target event label.
* Add ``event_inactivity`` method to ``MetaDataContainer`` to get inactivity segments between events.
* Add ``__version__`` variable to the module.
* Add ``check_installation`` function to check module installation.
* Add ``TUTAcousticScenes_2017_FeaturesSet`` dataset class.
* Add ``check_metadata`` method to dataset classes to double check meta and cross-validation setups automatically during the dataset initialization.

**Updates**

* Update ``ProcessingChain`` to verify that all items in the chain are instances of ``Processor`` class.
* Update ``ProbabilityItem`` to have index property.
* Update ``ProbabilityContainer`` to support pickle saving and loading.
* Update ``ProbabilityContainer`` to have ``as_matrix`` method.
* Update ``majority_vote`` method in ``DecisionEncoder`` to be more generic (works with both labels and class IDs).
* Move processor classes related to encoding into separate file.
* Update ``load`` method in ``MetaDataContainer`` to translate between decimal comma and point.
* Update ``data_collector`` function to be more generic.
* Update ``formatted_value`` method in ``FancyStringifier`` to support fixed length strings (``stf``).
* Refactor ``SubmissionChecker`` to be more flexible.
* Update ``DCASEAppParameterContainer`` to support secondary data processing chain.
* Update ``create_sequential_model`` function to return optionally functional API Keras model instead of default Keras sequential model.
* Update ``ProgressLoggerCallback`` to print estimate of the remaining model learning time.

**Bug fixes**

* Fix dataset class when no ``remote_file`` is set

v0.2.4
------

**New features**

* Add ``TUTUrbanAcousticScenes_2018_EvaluationSet`` and ``TUTUrbanAcousticScenes_2018_Mobile_EvaluationSet`` dataset classes.
* Add ``DCASE2018_Task5_EvaluationSet`` dataset class.

**Updates**

* Update ``formatted_value`` method in ``FancyStringifier`` to have full coverage of float formats (float precision from 1 to 4).

**Bug fixes**

* Fix ``TUTRareSoundEvents_2017_EvaluationSet`` dataset class to have correct audio path.

v0.2.3
------

**New features**

* Add ``AudioWritingProcessor`` and ``MonoAudioWritingProcessor`` processor classes.
* Add ``FeatureWritingProcessor`` and ``RepositoryFeatureWritingProcessor`` processor classes.

**Bug fixes**

* Fix ``DataRepository`` not to have internal variables in the ``__dict__`` after loading container from disk.

v0.2.2
------

In this version external dependencies of this module are minimized. External modules required for non-core functionality is not anymore included in the setup.py, and not automatically installed. Once user uses functionality requiring these rarely used external modules and module is not found, ImportError is raised with instructions to install correct module through pip. All module requirements are still available in ``requirements.txt``.

**New features**

* Add ``unique_source_labels`` property to ``MetaDataContainer``.
* Add ``file_format`` parameter to load and save method for ``ListContainer`` and ``DictContainer`` to force specific file format.
* Add  ``label_list`` parameter to ``ManyHotEncodingProcessor``.
* Add ``DatasetPacker`` class to make DCASE styled dataset packages.
* Add ``dataset_exists`` helper function to check Dataset classes.
* Add multi-channel audio example ``audio_container_ch4``.
* Add ``TUTUrbanAcousticScenes_2018_LeaderboardSet`` and ``TUTUrbanAcousticScenes_2018_Mobile_LeaderboardSet`` dataset classes.

**Updates**

* Update ``Dataset`` class handle also non-text file meta files by introducing parameter ``evaluation_setup_file_extension``.
* Update package list handling in ``Dataset`` to support custom package extraction parameters by extra parameter ``package_extract_parameters``.
* Update ``pad`` method in ``AudioContainer`` to work with multi-channel audio.
* Update ``compress`` method to produce split packages only if size limit is met.
* Update ``compress`` method to return package filenames.
* Update ``DCASE2018_Task5_DevelopmentSet`` dataset.

v0.2.1
------

**New features**

* Add ``md5`` and ``bytes`` properties to FileMixin.
* Add two level hierarchical balancing to ``validation_files_balanced`` method in ``AcousticSceneDataset``.
* Add ``TUTUrbanAcousticScenes_2018_DevelopmentSet`` and ``TUTUrbanAcousticScenes_2018_Mobile_DevelopmentSet`` datasets.
* Add ``float1_ci``, ``float2_ci``, ``float1_ci_bracket``, ``float2_ci_bracket``, ``float1_percentage+ci`` and ``float2_percentage+ci`` value types to ``formatted_value`` method in ``FancyStringifier``.
* Add ``get_set`` method to ``AppParameterContainer``.
* Add ``data_collector`` function to collect data and meta.

**Updates**

* Update ``debug_packages`` method in ``Dataset`` to provide more information.
* Update validation subset generation methods (``validation_split``, ``validation_files_dataset``, ``validation_files_random``, and ``validation_files_balanced``)  method in ``Dataset``, ``AcousticSceneDataset``, ``SoundEventDataset``, and ``AudioTaggingDataset`` to allow external processing of meta data before processing through ``training_meta`` parameter.
* Update ``filter`` method in ``ListDictContainer`` to allow filtering based on list of values.
* Update ``set_label`` property to ``MetaDataItem``.
* Update ``filter`` method in ``MetaDataContainer`` to use ``filter`` method from parent class.
* Update example applications to use current API.
* Update random seed setting for TensorFlow in ``setup_keras`` function.
* Update ``dataset_factory`` to handle dataset classes defined outside dcase_util.

**Bug fixes**

* Fix ``load_from_youtube`` method in ``AudioContainer``.
* Fix example applications to work on Windows (Python 3.6).

v0.2.0
------

**New features**

* Add ``row_reset`` and ``row_sep`` helper methods to ``FancyStringifier``, ``FancyLogger``, and ``FancyPrinter`` classes.

**Updates**

* Update ``download`` method in ``RemoteFile`` to be more robust when encounter SSL problems.
* Update ``AppParameterContainer`` to handle ``FEATURE_PROCESSING_CHAIN``, ``DATA_PROCESSING_CHAIN``.
* Update ``filter`` method in ``MetaDataContainer`` to accept ``source_label`` and ``source_label_list`` parameters.
* Update ``DCASE2018_Task5_DevelopmentSet``.

**Bug fixes**

* Fix ``construct_path`` method in ``ApplicationPaths`` to work in Windows as well.
* Fix path creation in ``AppParameterContainer``.

v0.1.9
------

**New features**

* Add new processors ``FeatureReadingProcessor``, ``DataShapingProcessor``, ``RepositoryAggregationProcessor``, ``RepositorySequencingProcessor``, and  ``RepositoryToMatrixProcessor``.
* Add extract method to ``SpectralFeatureExtractor``.
* Add automatic conversion of numeric fields when loading CSV data to ``ListDictContainer``.
* Add filter and get_field_unique methods to ``ListDictContainer``.
* Add MP4 to valid audio formats for ``AudioContainer``.
* Add general path modification method (``Path.modify``).
* Add Keras profile ``cuda0_fast``.
* Add Keras utility to create optimizer instance (`create_optimizer`).
* Add ``DCASE2018_Task5_DevelopmentSet`` and ``DCASE2013_Scenes_EvaluationSet`` datasets.
* Add ``DataMatrix4DContainer``.
* Add ``plot` method to ``DataMatrix3DContainer``.
* Add support for a new annotation format for tags [filename][tab][tags] in ``MetaDataContainer``.
* Add zero padding to ``Sequencer``.
* Add header field override in `load` method of ``MetaDataContainer``.
* Add support for new compressed audio formats (OGG, MP3) in ``AudioContainer``.
* Add ``segments`` method in ``AudioContainer`` to split signal into non-overlapping segments with optionally skipped regions.
* Add ``pad`` method in ``AudioContainer`` to pad signal into given length.
* Add ``compress`` method in ``PackageMixin``.
* Add ``Package`` class to handle local compressed file packages.
* Add ``change_axis`` method to ``DataMatrix2DContainer``, ``DataMatrix3DContainer``, and ``DataMatrix4DContainer``.
* Add ``KerasDataSequence`` class for data generation through processing chain.
* Add support for data and meta processing chains to ``DCASEAppParameterContainer``.
* Add ``many_hot`` method in ``DecisionEncoder``.

**Updates**

* Update ``TUTRareSoundEvents_2017_DevelopmentSet`` and ``TUTRareSoundEvents_2017_EvaluationSet`` datasets.
* Update Keras utility ``model_summary_string`` to use by default standard method from Keras.
* Update ``FeatureRepository`` API to be aligned with Container classes.
* Update ``Sequencer``, ``SequencingProcessor``, and ``RepositorySequencingProcessor`` API.
* Update ``AppParameterContainer`` to allow change of active set even after ``process`` method has been called.
* Update mechanism to store meta information about chain item when data is processed using processing chain.

**Bug fixes**

* Fix ``save`` method in ``MetaDataContainer`` when saving with tags in CSV format.
* Fix many methods to give more appropriate error messages.

API changes and compatibility

* ``Sequencer``, ``SequencingProcessor``, and ``RepositorySequencingProcessor`` API changes:
    * ``frames`` changed to ``sequence_length``
    * ``hop_length_frames`` to ``hop_length``
    * ``padding`` parameter accepts now strings (``zero`` and ``repeat``)

v0.1.8
------

**New features**

* Add new formats for ``MetaDataContainer`` (cpickle, CSV).
* Add forced file formats when reading and saving containers.
* Add Keras setup function.
* Add frame splitting method into ``AudioContainer``.

**Bug fixes**

* Fix unicode string support when printing container information.
* Fix data contamination through data references while manipulating data.
* Some minor bug fixes.

v0.1.7
------

**New features**

* Add intersection method for ``MetaDataContainer``.

**Updates**

* Update dataset class API (e.g. copy returned metadata prevent accidental manipulation, uniform method names).

**Bug fixes**

* Fix data sequencing when overlapping sequencing is used.
* Fix datasets ``CHiMEHome_DomesticAudioTag_DevelopmentSet``, ``TUTAcousticScenes_2017_EvaluationSet``, and ``TUTSoundEvents_2017_EvaluationSet``.

v0.1.6
------

**New features**

* Add ``CHiMEHome_DomesticAudioTag_EvaluationSet`` dataset.

**Updates**

* Update example audio to be 16-bit audio file in wav-format instead of FLAC used earlier.
* Update ``ProbabilityContainer`` API to be more compatible with ``MetaDataContainer``.
* Update ``MetaDataItem`` to be compatible with field naming used previously in DCASE baseline systems.
* Update ui utilities.

**Bug fixes**

* Fix audio reading when target sampling rate is not set.
* Some minor bug fixes.

v0.1.5
------

* Fixing PYPI package.

v0.1.4
------

* Release first PYPI package.

v0.1.0
------

* Initial public release.