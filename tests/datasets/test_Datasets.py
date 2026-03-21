""" Unit tests for Datasets """
import os
import dcase_util
import tempfile
from dcase_util.datasets import Dataset
from dcase_util.containers import MetaDataContainer

content = [
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'speech',
            'onset': 1.0,
            'offset': 10.0,
        },
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'mouse clicking',
            'onset': 3.0,
            'offset': 5.0,
        },
        {
            'filename': 'audio_001.wav',
            'scene_label': 'office',
            'event_label': 'printer',
            'onset': 7.0,
            'offset': 9.0,
        },
        {
            'filename': 'audio_002.wav',
            'scene_label': 'meeting',
            'event_label': 'speech',
            'onset': 1.0,
            'offset': 9.0,
        },
        {
            'filename': 'audio_002.wav',
            'scene_label': 'meeting',
            'event_label': 'printer',
            'onset': 5.0,
            'offset': 7.0,
        },
    ]

def test_dataset():
    d = Dataset()
    d.meta_container = MetaDataContainer(content)

    assert d.scene_labels() == ['meeting', 'office']
    assert d.scene_label_count() == 2
    assert d.event_labels() == ['mouse clicking', 'printer', 'speech']
    assert d.event_label_count() == 3

    assert d.meta_count == len(content)
    assert d.meta == content

    assert d.file_meta(filename='audio_001.wav') == [content[0], content[1], content[2]]
    assert d.file_meta(filename='audio_002.wav') == [content[3], content[4]]

def test_dataset_construction():
    dcase_util.datasets.TUTUrbanAcousticScenes_2018_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTUrbanAcousticScenes_2018_Mobile_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTAcousticScenes_2017_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTAcousticScenes_2017_EvaluationSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTRareSoundEvents_2017_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTRareSoundEvents_2017_EvaluationSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTSoundEvents_2017_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTSoundEvents_2017_EvaluationSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTAcousticScenes_2016_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTAcousticScenes_2016_EvaluationSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTSoundEvents_2016_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUTSoundEvents_2016_EvaluationSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.TUT_SED_Synthetic_2016(
        included_content_types=['meta']
    )

    dcase_util.datasets.DCASE2013_Scenes_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.CHiMEHome_DomesticAudioTag_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.DCASE2017_Task4tagging_DevelopmentSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.DCASE2017_Task4tagging_EvaluationSet(
        included_content_types=['meta']
    )

    dcase_util.datasets.DCASE2018_Task5_DevelopmentSet(
        included_content_types=['meta']
    )

def test_TUTAcousticScenes_2016_DevelopmentSet():
    db = dcase_util.datasets.TUTAcousticScenes_2016_DevelopmentSet(
        included_content_types=['meta']
    ).initialize()

    # Cross-validation setup / Train
    assert db.train().file_count == 1170
    assert db.train(1).file_count == 880
    assert db.train(2).file_count == 880
    assert db.train(3).file_count == 872
    assert db.train(4).file_count == 878

    # Cross-validation setup / Test
    assert db.test().file_count == 1170
    assert db.test(1).file_count == 290
    assert db.test(2).file_count == 290
    assert db.test(3).file_count == 298
    assert db.test(4).file_count == 292

    assert db.eval().file_count == 1170
    assert db.eval(1).file_count == 290
    assert db.eval(2).file_count == 290
    assert db.eval(3).file_count == 298
    assert db.eval(4).file_count == 292

    assert set(db.train_files(1)).intersection(db.test_files(1)) == set()
    assert set(db.train_files(2)).intersection(db.test_files(2)) == set()
    assert set(db.train_files(3)).intersection(db.test_files(3)) == set()
    assert set(db.train_files(4)).intersection(db.test_files(4)) == set()

    assert db.audio_files == []
    assert db.audio_file_count == 0

    assert len(db.meta) == 1170
    assert db.meta_count == 1170

    assert db.fold_count == 4

    assert db.scene_labels() == ['beach',
                                       'bus',
                                       'cafe/restaurant',
                                       'car',
                                       'city_center',
                                       'forest_path',
                                       'grocery_store',
                                       'home',
                                       'library',
                                       'metro_station',
                                       'office',
                                       'park',
                                       'residential_area',
                                       'train',
                                       'tram']
    assert db.scene_label_count() == 15

    assert db.check_filelist() == True

    assert db.folds() == [1, 2, 3, 4]
    assert db.folds('full') == ['all_data']

    with dcase_util.utils.DisableLogger():
        db.log()

def test_TUTAcousticScenes_2016_EvaluationSet():
    db = dcase_util.datasets.TUTAcousticScenes_2016_EvaluationSet(
        included_content_types=['meta']
    ).initialize()

    # Cross-validation setup / Train
    assert db.train().file_count == 0

    # Cross-validation setup / Test
    assert db.test().file_count == 390

    assert db.eval().file_count == 390

    assert db.audio_files == []
    assert db.audio_file_count == 0

    assert len(db.meta) == 390
    assert db.meta_count == 390

    assert db.fold_count == None

    assert db.scene_label_count() == 15

    assert db.check_filelist() == True

    assert db.folds() == ['all_data']
    assert db.folds('full') == ['all_data']

    with dcase_util.utils.DisableLogger():
        db.log()

def test_TUTAcousticScenes_2017_DevelopmentSet():
    db = dcase_util.datasets.TUTAcousticScenes_2017_DevelopmentSet(
        included_content_types=['meta']
    ).initialize()

    audio_path = os.path.join(
        tempfile.gettempdir(),
        'dcase_util_datasets',
        db.storage_name,
        'audio'
    )

    # Cross-validation setup / Train
    assert db.train().file_count == 4680
    assert db.train(1).file_count == 3510
    assert db.train(2).file_count == 3507
    assert db.train(3).file_count == 3507
    assert db.train(4).file_count == 3510

    assert db.train_files()[0] == os.path.join(audio_path, 'a001_0_10.wav')
    assert db.train_files(1)[0] == os.path.join(audio_path, 'a001_0_10.wav')
    assert db.train_files(2)[0] == os.path.join(audio_path, 'a001_0_10.wav')
    assert db.train_files(3)[0] == os.path.join(audio_path, 'a001_0_10.wav')
    assert db.train_files(4)[0] == os.path.join(audio_path, 'a002_0_10.wav')

    # Cross-validation setup / Test
    assert db.test().file_count == 4680
    assert db.test(1).file_count == 1170
    assert db.test(2).file_count == 1173
    assert db.test(3).file_count == 1173
    assert db.test(4).file_count == 1170

    assert db.test_files()[0] == os.path.join(audio_path, 'a001_0_10.wav')
    assert db.test_files(1)[0] == os.path.join(audio_path, 'a002_0_10.wav')
    assert db.test_files(2)[0] == os.path.join(audio_path, 'a005_0_10.wav')
    assert db.test_files(3)[0] == os.path.join(audio_path, 'a010_0_10.wav')
    assert db.test_files(4)[0] == os.path.join(audio_path, 'a001_0_10.wav')

    assert db.eval().file_count == 4680
    assert db.eval(1).file_count == 1170
    assert db.eval(2).file_count == 1173
    assert db.eval(3).file_count == 1173
    assert db.eval(4).file_count == 1170

    assert db.eval_files()[0] == os.path.join(audio_path, 'a001_0_10.wav')
    assert db.eval_files(1)[0] == os.path.join(audio_path, 'a002_0_10.wav')
    assert db.eval_files(2)[0] == os.path.join(audio_path, 'a005_0_10.wav')
    assert db.eval_files(3)[0] == os.path.join(audio_path, 'a010_0_10.wav')
    assert db.eval_files(4)[0] == os.path.join(audio_path, 'a001_0_10.wav')

    assert set(db.train_files(1)).intersection(db.test_files(1)) == set()
    assert set(db.train_files(2)).intersection(db.test_files(2)) == set()
    assert set(db.train_files(3)).intersection(db.test_files(3)) == set()
    assert set(db.train_files(4)).intersection(db.test_files(4)) == set()

    assert db[0].filename == os.path.join(audio_path, 'b020_90_100.wav')
    assert db[0].scene_label == 'beach'

    assert db.audio_files == []
    assert db.audio_file_count == 0

    assert len(db.meta) == 4680
    assert db.meta_count == 4680

    assert len(db.error_meta) == 84
    assert db.error_meta_count == 84

    assert db.fold_count == 4

    assert db.scene_labels() == ['beach',
                                       'bus',
                                       'cafe/restaurant',
                                       'car',
                                       'city_center',
                                       'forest_path',
                                       'grocery_store',
                                       'home',
                                       'library',
                                       'metro_station',
                                       'office',
                                       'park',
                                       'residential_area',
                                       'train',
                                       'tram']
    assert db.scene_label_count() == 15

    assert db.check_filelist() == True

    with dcase_util.utils.DisableLogger():
        rand_train, rand_validation = db.validation_split(
            fold=1,
            validation_amount=0.5,
            split_type='random',
            iterations=10,
            verbose=False
        )

    assert set(rand_train).intersection(rand_validation) == set()

    with dcase_util.utils.DisableLogger():
        bal_train, bal_validation = db.validation_split(
            fold=1,
            validation_amount=0.5,
            split_type='balanced',
            iterations=10,
            verbose=False
        )

    assert set(bal_train).intersection(bal_validation) == set()

    assert db.folds() == [1, 2, 3, 4]
    assert db.folds('full') == ['all_data']

    assert db.file_error_meta(filename='audio/b079_180_190.wav')[0].filename == 'audio/b079_180_190.wav'
    assert db.file_error_meta(filename='audio/b079_180_190.wav')[0].event_label == 'error'
    assert db.file_error_meta(filename='audio/b079_180_190.wav')[0].onset == 1.991448
    assert db.file_error_meta(filename='audio/b079_180_190.wav')[0].offset == 2.446579

    assert db.relative_to_absolute_path('audio/b079_180_190.wav') == os.path.join(audio_path, 'b079_180_190.wav')

    assert db.absolute_to_relative_path(os.path.join(audio_path, 'b079_180_190.wav')) == os.path.join('audio', 'b079_180_190.wav')

    assert db.dataset_bytes() == 10700420548
    assert db.dataset_size_string() == '9.966 GB'
    assert db.dataset_size_on_disk() == '969.1 KB'

    with dcase_util.utils.DisableLogger():
        db.log()

def test_TUTAcousticScenes_2017_EvaluationSet():
    db = dcase_util.datasets.TUTAcousticScenes_2017_EvaluationSet(
        included_content_types=['meta']
    ).initialize()

    # Cross-validation setup / Train
    assert db.train().file_count == 0

    # Cross-validation setup / Test
    assert db.test().file_count == 1620

    assert db.eval().file_count == 1620

    assert db.audio_files == []
    assert db.audio_file_count == 0

    assert len(db.meta) == 1620
    assert db.meta_count == 1620

    assert db.fold_count == None

    assert db.scene_label_count() == 15

    assert db.check_filelist() == True

    assert db.folds() == ['all_data']
    assert db.folds('full') == ['all_data']

    with dcase_util.utils.DisableLogger():
        db.log()

def test_TUTUrbanAcousticScenes_2018_DevelopmentSet():
   db = dcase_util.datasets.TUTUrbanAcousticScenes_2018_DevelopmentSet(
       included_content_types=['meta']
   ).initialize()

   # Cross-validation setup / Train
   assert db.train().file_count == 8640
   assert db.train(1).file_count == 6122

   # Cross-validation setup / Test
   assert db.test().file_count == 8640
   assert db.test(1).file_count == 2518

   assert db.eval().file_count == 8640
   assert db.eval(1).file_count == 2518

   assert set(db.train_files(1)).intersection(db.test_files(1)) == set()
   assert db.audio_files == []
   assert db.audio_file_count == 0
   assert len(db.meta) == 8640
   assert db.meta_count == 8640
   assert db.fold_count == 1
   assert db.scene_label_count() == 10
   assert db.check_filelist() == True

   with dcase_util.utils.DisableLogger():
       bal_train, bal_validation = db.validation_split(
           fold=1,
           validation_amount=0.5,
           split_type='balanced',
           iterations=10,
           verbose=False
       )

   assert set(bal_train).intersection(bal_validation) == set()
   assert db.folds() == [1]
   assert db.folds('full') == ['all_data']

   with dcase_util.utils.DisableLogger():
       db.log()

def test_TUTUrbanAcousticScenes_2018_Mobile_DevelopmentSet():
   db = dcase_util.datasets.TUTUrbanAcousticScenes_2018_Mobile_DevelopmentSet(
       included_content_types=['meta']
   ).initialize()

   # Cross-validation setup / Train
   assert db.train().file_count == 10080
   assert db.train(1).file_count == 7202

   # Cross-validation setup / Test
   assert db.test().file_count == 10080
   assert db.test(1).file_count == 2878

   assert db.eval().file_count == 10080
   assert db.eval(1).file_count == 2878

   assert set(db.train_files(1)).intersection(db.test_files(1)) == set()
   assert db.audio_files == []
   assert db.audio_file_count == 0
   assert len(db.meta) == 10080
   assert db.meta_count == 10080
   assert db.fold_count == 1
   assert db.scene_label_count() == 10
   assert db.check_filelist() == True
   assert db.folds() == [1]
   assert db.folds('full') == ['all_data']
   with dcase_util.utils.DisableLogger():
       db.log()

def test_TUTSoundEvents_2016_DevelopmentSet():
    db = dcase_util.datasets.TUTSoundEvents_2016_DevelopmentSet(
        included_content_types=['meta']
    ).initialize()

    # Cross-validation setup / Train
    assert db.train().file_count == 22
    assert db.train(1).file_count == 16
    assert db.train(2).file_count == 16
    assert db.train(3).file_count == 17
    assert db.train(4).file_count == 17

    # Cross-validation setup / Test
    assert db.test().file_count == 22
    assert db.test(1).file_count == 6
    assert db.test(2).file_count == 6
    assert db.test(3).file_count == 5
    assert db.test(4).file_count == 5

    assert db.eval().file_count == 22
    assert db.eval(1).file_count == 6
    assert db.eval(2).file_count == 6
    assert db.eval(3).file_count == 5
    assert db.eval(4).file_count == 5

    assert set(db.train_files(1)).intersection(db.test_files(1)) == set()
    assert set(db.train_files(2)).intersection(db.test_files(2)) == set()
    assert set(db.train_files(3)).intersection(db.test_files(3)) == set()
    assert set(db.train_files(4)).intersection(db.test_files(4)) == set()

    assert len(db.meta) == 954
    assert db.meta_count == 954

    assert db.scene_labels() == ['home', 'residential_area']
    assert db.scene_label_count() == 2

    assert db.event_labels() == ['(object) banging', '(object) rustling', '(object) snapping', 'bird singing', 'car passing by', 'children shouting', 'cupboard', 'cutlery', 'dishes', 'drawer', 'glass jingling', 'object impact', 'people speaking', 'people walking', 'washing dishes', 'water tap running', 'wind blowing']

    assert db.event_label_count() == 17

    assert db.check_filelist() == True

    assert db.folds() == [1, 2, 3, 4]
    assert db.folds('full') == ['all_data']

def test_TUTSoundEvents_2016_EvaluationSet():
    db = dcase_util.datasets.TUTSoundEvents_2016_EvaluationSet(
        included_content_types=['meta']
    ).initialize()

    # Cross-validation setup / Test
    assert db.test().file_count == 10

    assert db.eval().file_count == 10

    assert len(db.meta) == 511
    assert db.meta_count == 511

    assert db.scene_labels() == ['home', 'residential_area']
    assert db.scene_label_count() == 2

    assert db.event_labels() == ['(object) banging', '(object) rustling', '(object) snapping', 'bird singing', 'car passing by',
                    'children shouting', 'cupboard', 'cutlery', 'dishes', 'drawer', 'glass jingling', 'object impact',
                    'people speaking', 'people walking', 'washing dishes', 'water tap running', 'wind blowing']

    assert db.event_label_count() == 17

    assert db.check_filelist() == True

    assert db.folds() == ['all_data']
    assert db.folds('full') == ['all_data']

def test_TUTSoundEvents_2017_DevelopmentSet():
   db = dcase_util.datasets.TUTSoundEvents_2017_DevelopmentSet(
       included_content_types=['meta']
   ).initialize()

   audio_path = os.path.join(
       tempfile.gettempdir(),
       'dcase_util_datasets',
       db.storage_name,
       'audio',
       'street'
   )

   # Cross-validation setup / Train
   assert db.train().file_count == 24
   assert db.train(1).file_count == 18
   assert db.train(2).file_count == 18
   assert db.train(3).file_count == 18
   assert db.train(4).file_count == 18

   assert db.train_files()[0] == os.path.join(audio_path, 'a001.wav')
   assert db.train_files(1)[0] == os.path.join(audio_path, 'a001.wav')
   assert db.train_files(2)[0] == os.path.join(audio_path, 'a001.wav')
   assert db.train_files(3)[0] == os.path.join(audio_path, 'a001.wav')
   assert db.train_files(4)[0] == os.path.join(audio_path, 'a003.wav')

   # Cross-validation setup / Test
   assert db.test().file_count == 24
   assert db.test(1).file_count == 6
   assert db.test(2).file_count == 6
   assert db.test(3).file_count == 6
   assert db.test(4).file_count == 6

   assert db.test_files()[0] == os.path.join(audio_path, 'a001.wav')
   assert db.test_files(1)[0] == os.path.join(audio_path, 'a010.wav')
   assert db.test_files(2)[0] == os.path.join(audio_path, 'a003.wav')
   assert db.test_files(3)[0] == os.path.join(audio_path, 'a008.wav')
   assert db.test_files(4)[0] == os.path.join(audio_path, 'a001.wav')

   assert db.eval().file_count == 24
   assert db.eval(1).file_count == 6
   assert db.eval(2).file_count == 6
   assert db.eval(3).file_count == 6
   assert db.eval(4).file_count == 6

   assert db.eval_files()[0] == os.path.join(audio_path, 'a001.wav')
   assert db.eval_files(1)[0] == os.path.join(audio_path, 'a010.wav')
   assert db.eval_files(2)[0] == os.path.join(audio_path, 'a003.wav')
   assert db.eval_files(3)[0] == os.path.join(audio_path, 'a008.wav')
   assert db.eval_files(4)[0] == os.path.join(audio_path, 'a001.wav')

   assert set(db.train_files(1)).intersection(db.test_files(1)) == set()
   assert set(db.train_files(2)).intersection(db.test_files(2)) == set()
   assert set(db.train_files(3)).intersection(db.test_files(3)) == set()
   assert set(db.train_files(4)).intersection(db.test_files(4)) == set()

   assert db[0].filename == os.path.join(audio_path, 'a001.wav')
   assert db[0].scene_label == 'street'
   assert db[0].event_label == 'people walking'
   assert db[0].onset == 1.589213
   assert db[0].offset == 2.38382

   assert len(db.meta) == 659
   assert db.meta_count == 659
   assert db.scene_labels() == ['street']
   assert db.scene_label_count() == 1
   assert db.event_labels() == ['brakes squeaking',
                                      'car',
                                      'children',
                                      'large vehicle',
                                      'people speaking',
                                      'people walking']

   assert db.event_label_count() == 6
   assert db.check_filelist() == True

   with dcase_util.utils.DisableLogger():
       rand_train, rand_validation = db.validation_split(
           fold=1,
           validation_amount=0.5,
           split_type='random',
           verbose=False
       )

   assert set(rand_train).intersection(rand_validation) == set()

   with dcase_util.utils.DisableLogger():
       bal_train, bal_validation = db.validation_split(
           fold=1,
           validation_amount=0.5,
           split_type='balanced',
           iterations=10,
           verbose=False
       )

   assert set(bal_train).intersection(bal_validation) == set()
   assert db.folds() == [1, 2, 3, 4]
   assert db.folds('full') == ['all_data']
   assert db.dataset_bytes() == 1276082461
   assert db.dataset_size_string() == '1.188 GB'
   assert db.dataset_size_on_disk() == '642.2 KB'

def test_TUTSoundEvents_2017_EvaluationSet():
   db = dcase_util.datasets.TUTSoundEvents_2017_EvaluationSet(
       included_content_types=['meta']
   ).initialize()

   # Cross-validation setup / Test
   assert db.test().file_count == 8

   assert db.eval().file_count == 8

   assert len(db.meta) == 247
   assert db.meta_count == 247

   assert db.scene_labels() == ['street']
   assert db.scene_label_count() == 1

   assert db.event_labels() == ['brakes squeaking',
                                      'car',
                                      'children',
                                      'large vehicle',
                                      'people speaking',
                                      'people walking']

   assert db.event_label_count() == 6

   assert db.check_filelist() == True

   assert db.folds() == ['all_data']
   assert db.folds('full') == ['all_data']

