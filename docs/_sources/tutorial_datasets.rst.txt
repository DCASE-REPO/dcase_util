.. _tutorial_datasets:

Datasets
--------

Dataset classes are provided in the library to create uniform interface for many differently organized audio datasets.
The datasets are downloaded, extracted and prepared for usage when they are first time used.

Four type of datasets are provided:

- **Acoustic scene datasets**, classes inherited from `dcase_util.datasets.AcousticSceneDataset` class.
- **Sound event datasets**, classes inherited from `dcase_util.datasets.SoundEventDataset` class.
- **Sound event datasets with synthetic data creation**, classes inherited from `dcase_util.datasets.SyntheticSoundEventDataset` class.
- **Audio tagging datasets**, classes inherited from `dcase_util.datasets.AudioTaggingDataset` class.

To get list of all datasets available::

    print(dcase_util.datasets.dataset_list())
    #  Dataset list
    #  Class Name                                 | Group | Remote | Local  | Audio | Scenes | Events | Tags
    #  ------------------------------------------ | ----- | ------ | ------ | ----- | ------ | ------ | ----
    #  DCASE2013_Scenes_DevelopmentSet            | scene | 344 MB | 849 MB | 100   | 10     |        |
    #  TUTAcousticScenes_2016_DevelopmentSet      | scene | 7 GB   | 23 GB  | 1170  | 15     |        |
    #  TUTAcousticScenes_2016_EvaluationSet       | scene | 2 GB   | 5 GB   | 390   | 15     |        |
    #  TUTAcousticScenes_2017_DevelopmentSet      | scene | 9 GB   | 21 GB  | 4680  | 15     |        |
    #  TUTAcousticScenes_2017_EvaluationSet       | scene | 3 GB   | 7 GB   |       |        |        |
    #  DCASE2017_Task4tagging_DevelopmentSet      | event | 5 MB   | 24 GB  | 56700 | 1      | 17     |
    #  DCASE2017_Task4tagging_EvaluationSet       | event | 823 MB | 1 GB   |       |        |        |
    #  TUTRareSoundEvents_2017_DevelopmentSet     | event | 7 GB   | 28 GB  |       |        | 3      |
    #  TUTRareSoundEvents_2017_EvaluationSet      | event | 4 GB   | 4 GB   |       |        | 3      |
    #  TUTSoundEvents_2016_DevelopmentSet         | event | 967 MB | 2 GB   | 954   | 2      | 17     |
    #  TUTSoundEvents_2016_EvaluationSet          | event | 449 MB | 989 MB | 511   | 2      | 17     |
    #  TUTSoundEvents_2017_DevelopmentSet         | event | 1 GB   | 2 GB   | 659   | 1      | 6      |
    #  TUTSoundEvents_2017_EvaluationSet          | event | 370 MB | 798 MB |       |        |        |
    #  TUT_SED_Synthetic_2016                     | event | 4 GB   | 5 GB   |       |        |        |
    #  CHiMEHome_DomesticAudioTag_DevelopmentSet  | tag   | 3 GB   | 9 GB   | 1946  | 1      |        | 7

Initializing dataset
====================

To download, extract and prepare dataset (in this case dataset will be place in the temp dir,
and only files related to meta data are downloaded)::

    import tempfile

    db = dcase_util.datasets.TUTAcousticScenes_2016_DevelopmentSet(
        data_path=tempfile.gettempdir(),
        included_content_types=['meta']
    )
    db.initialize()
    db.show()
    # DictContainer :: Class
    #   audio_source                      : Field recording
    #   audio_type                        : Natural
    #   authors                           : Annamaria Mesaros, Toni Heittola, and Tuomas Virtanen
    #   licence                           : free non-commercial
    #   microphone_model                  : Soundman OKM II Klassik/studio A3 electret microphone
    #   recording_device_model            : Roland Edirol R-09
    #   title                             : TUT Acoustic Scenes 2016, development dataset
    #   url                               : https://zenodo.org/record/45739
    #
    # MetaDataContainer :: Class
    #   Filename                          : /tmp/TUT-acoustic-scenes-2016-development/meta.txt
    #   Items                             : 1170
    #   Unique
    #     Files                           : 1170
    #     Scene labels                    : 15
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         beach                      78
    #         bus                        78
    #         cafe/restaurant            78
    #         car                        78
    #         city_center                78
    #         forest_path                78
    #         grocery_store              78
    #         home                       78
    #         library                    78
    #         metro_station              78
    #         office                     78
    #         park                       78
    #         residential_area           78
    #         train                      78
    #         tram                       78


Cross-validation setup
======================

Usually dataset are delivered with cross-validation setup.

To get training material for the fold 1::

    training_material = db.train(fold=1)
    training_material.show()
    # MetaDataContainer :: Class
    #   Filename                          : /tmp/TUT-acoustic-scenes-2016-development/evaluation_setup/fold1_train.txt
    #   Items                             : 880
    #   Unique
    #     Files                           : 880
    #     Scene labels                    : 15
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         beach                      59
    #         bus                        59
    #         cafe/restaurant            60
    #         car                        58
    #         city_center                60
    #         forest_path                57
    #         grocery_store              59
    #         home                       56
    #         library                    57
    #         metro_station              59
    #         office                     59
    #         park                       58
    #         residential_area           59
    #         train                      60
    #         tram                       60

To get testing material for the fold 1 (material without reference data)::

    testing_material = db.test(fold=1)
    testing_material.show()
    # MetaDataContainer :: Class
    #   Filename                          : /tmp/TUT-acoustic-scenes-2016-development/evaluation_setup/fold1_test.txt
    #   Items                             : 290
    #   Unique
    #     Files                           : 290
    #     Scene labels                    : 0
    #     Event labels                    : 0
    #     Tags                            : 0

To get testing material for the fold 1 with full reference data::

    eval_material = db.eval(fold=1)
    eval_material.show()

    # MetaDataContainer :: Class
    #   Filename                          : /tmp/TUT-acoustic-scenes-2016-development/evaluation_setup/fold1_evaluate.txt
    #   Items                             : 290
    #   Unique
    #     Files                           : 290
    #     Scene labels                    : 15
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         beach                      19
    #         bus                        19
    #         cafe/restaurant            18
    #         car                        20
    #         city_center                18
    #         forest_path                21
    #         grocery_store              19
    #         home                       22
    #         library                    21
    #         metro_station              19
    #         office                     19
    #         park                       20
    #         residential_area           19
    #         train                      18
    #         tram                       18

To get all data set fold to None::

    all_material = db.train(fold=None)
    all_material.show()
    # MetaDataContainer :: Class
    #   Filename                          : /tmp/TUT-acoustic-scenes-2016-development/meta.txt
    #   Items                             : 1170
    #   Unique
    #     Files                           : 1170
    #     Scene labels                    : 15
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         beach                      78
    #         bus                        78
    #         cafe/restaurant            78
    #         car                        78
    #         city_center                78
    #         forest_path                78
    #         grocery_store              78
    #         home                       78
    #         library                    78
    #         metro_station              78
    #         office                     78
    #         park                       78
    #         residential_area           78
    #         train                      78
    #         tram                       78


Iterating over all folds::

    for fold in db.folds:
        train_material = db.train(fold=fold)

Most of the datasets do not provide validation set split. However, dataset class provides a few way to
generate it from the training set while maintaining the data statistics and making sure there will not be data
from same source in both training and validation set.

Generating **balanced** validation set (balancing done so that recording from same location are assigned to same set) for fold 1::

    training_files, validation_files = db.validation_split(
        fold=1,
        split_type='balanced',
        validation_amount=0.3
    )

Generating **random** validation set (without balancing) for fold 1::

    training_files, validation_files = db.validation_split(
        fold=1,
        split_type='random',
        validation_amount=0.3
    )

Getting validation set provided with dataset (dataset used in the example does not provide it, and this will raise an error.)::

    training_files, validation_files = db.validation_split(
        fold=1,
        split_type='dataset'
    )

Meta data
=========

Getting meta data associated to the file::

    items = db.file_meta(filename='audio/b086_150_180.wav')
    print(items)
    # MetaDataContainer :: Class
    #   Items                             : 1
    #   Unique
    #     Files                           : 1
    #     Scene labels                    : 1
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         audio/b086_150_180..        -        -   grocery_store     -                 -                 -
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         grocery_store               1


