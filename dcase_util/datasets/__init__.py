# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Datasets
========
Classes for dataset handling

Dataset
-------

*dcase_util.datasets.Dataset*

This is the base class, and all the specialized datasets are inherited from it. One should never use base class itself.

Usage examples:

.. code-block:: python
    :linenos:

    # Create class
    dataset = TUTAcousticScenes_2017_DevelopmentSet(data_path='data')
    # Initialize dataset, this will make sure dataset is downloaded, packages are extracted,
    # and needed meta files are created
    dataset.initialize()
    # Show meta data
    dataset.meta.show()
    # Get all evaluation setup folds
    folds = dataset.folds()
    # Get all evaluation setup folds
    train_data_fold1 = dataset.train(fold=folds[0])
    test_data_fold1 = dataset.test(fold=folds[0])

.. autosummary::
    :toctree: generated/

    Dataset
    Dataset.initialize
    Dataset.download_packages
    Dataset.extract_packages
    Dataset.debug_packages
    Dataset.prepare
    Dataset.process_meta_item

    Dataset.check_filelist

    Dataset.show
    Dataset.log

    Dataset.load
    Dataset.load_meta
    Dataset.load_crossvalidation_data

    Dataset.audio_files
    Dataset.audio_file_count

    Dataset.meta
    Dataset.meta_count

    Dataset.error_meta
    Dataset.error_meta_count

    Dataset.folds
    Dataset.fold_count

    Dataset.evaluation_setup_filename

    Dataset.train
    Dataset.test
    Dataset.eval

    Dataset.train_files
    Dataset.test_files
    Dataset.eval_files

    Dataset.validation_split
    Dataset.validation_files_dataset
    Dataset.validation_files_random
    Dataset.validation_files_balanced

    Dataset.scene_labels
    Dataset.scene_label_count

    Dataset.event_labels
    Dataset.event_label_count

    Dataset.tags
    Dataset.tag_count

    Dataset.file_meta
    Dataset.file_error_meta
    Dataset.file_features

    Dataset.relative_to_absolute_path
    Dataset.absolute_to_relative_path

    Dataset.dataset_bytes
    Dataset.dataset_size_string
    Dataset.dataset_size_on_disk

AcousticSceneDataset
--------------------

*dcase_util.datasets.AcousticSceneDataset*

.. autosummary::
    :toctree: generated/

    AcousticSceneDataset

Specialized classes inherited AcousticSceneDataset:

.. autosummary::
    :toctree: generated/

    TUTAcousticScenes_2016_DevelopmentSet
    TUTAcousticScenes_2016_EvaluationSet
    TUTAcousticScenes_2017_DevelopmentSet
    TUTAcousticScenes_2017_EvaluationSet
    TUTAcousticScenes_2017_FeaturesSet
    TUTUrbanAcousticScenes_2018_DevelopmentSet
    TUTUrbanAcousticScenes_2018_LeaderboardSet
    TUTUrbanAcousticScenes_2018_EvaluationSet
    TUTUrbanAcousticScenes_2018_Mobile_DevelopmentSet
    TUTUrbanAcousticScenes_2018_Mobile_LeaderboardSet
    TUTUrbanAcousticScenes_2018_Mobile_EvaluationSet
    TAUUrbanAcousticScenes_2019_DevelopmentSet
    TAUUrbanAcousticScenes_2019_LeaderboardSet
    TAUUrbanAcousticScenes_2019_EvaluationSet
    TAUUrbanAcousticScenes_2019_Mobile_DevelopmentSet
    TAUUrbanAcousticScenes_2019_Mobile_LeaderboardSet
    TAUUrbanAcousticScenes_2019_Mobile_EvaluationSet
    TAUUrbanAcousticScenes_2019_Openset_DevelopmentSet
    TAUUrbanAcousticScenes_2019_Openset_LeaderboardSet
    TAUUrbanAcousticScenes_2019_Openset_EvaluationSet
    TAUUrbanAcousticScenes_2020_Mobile_DevelopmentSet
    TAUUrbanAcousticScenes_2020_3Class_DevelopmentSet
    DCASE2018_Task5_DevelopmentSet
    DCASE2018_Task5_EvaluationSet

SoundEventDataset
-----------------

*dcase_util.datasets.SoundEventDataset*

.. autosummary::
    :toctree: generated/

    SoundEventDataset
    SoundEventDataset.event_label_count
    SoundEventDataset.event_labels
    SoundEventDataset.train
    SoundEventDataset.test

Specialized classes inherited SoundEventDataset:

.. autosummary::
    :toctree: generated/

    TUTRareSoundEvents_2017_DevelopmentSet
    TUTRareSoundEvents_2017_EvaluationSet
    TUTSoundEvents_2017_DevelopmentSet
    TUTSoundEvents_2017_EvaluationSet
    TUTSoundEvents_2016_DevelopmentSet
    TUTSoundEvents_2016_EvaluationSet
    TUT_SED_Synthetic_2016

AudioTaggingDataset
-------------------

*dcase_util.datasets.AudioTaggingDataset*

.. autosummary::
    :toctree: generated/

    AudioTaggingDataset
    DCASE2017_Task4tagging_DevelopmentSet
    DCASE2017_Task4tagging_EvaluationSet
    CHiMEHome_DomesticAudioTag_DevelopmentSet

Helpers
-------

*dcase_util.datasets.*

Helper functions to access Dataset classes.

.. autosummary::
    :toctree: generated/

    dataset_list
    dataset_factory
    dataset_exists

"""

from .datasets import *
from .dcase2013 import *
from .dcase2016 import *
from .dcase2017 import *
from .dcase2018 import *
from .tut import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
