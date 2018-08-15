# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os

import numpy

from dcase_util.datasets import AcousticSceneDataset
from dcase_util.containers import MetaDataContainer, MetaDataItem
from dcase_util.utils import Path


class DCASE2013_Scenes_DevelopmentSet(AcousticSceneDataset):
    """DCASE2013 Acoustic scenes 2013 development dataset

    This dataset was used in DCASE2013 - Task 1, Acoustic scene classification

    """

    def __init__(self,
                 storage_name='DCASE2013-acoustic-scenes-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'DCASE2013-acoustic-scenes-development'

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.
            Default value None

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.
            Default value None

        """

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['dataset_group'] = 'scene'
        kwargs['dataset_meta'] = {
            'authors': 'D. Giannoulis, E. Benetos, D. Stowell, and M. D. Plumbley',
            'title': 'IEEE AASP CASA Challenge - Public Dataset for Scene Classification Task',
            'url': 'https://archive.org/details/dcase2013_scene_classification',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Unknown',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
        }
        kwargs['crossvalidation_folds'] = 5
        kwargs['package_list'] = [
            {
                'content_type': ['audio', 'meta', 'documentation'],
                'remote_file': 'https://archive.org/download/dcase2013_scene_classification/scenes_stereo.zip',
                'remote_bytes': 361748263,
                'remote_md5': 'abdefde136d84de33b0f20a0f13a6b97',
                'filename': 'scenes_stereo.zip'
            }
        ]
        kwargs['audio_paths'] = [
            'scenes_stereo'
        ]
        super(DCASE2013_Scenes_DevelopmentSet, self).__init__(**kwargs)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if not self.meta_container.exists():
            meta_data = MetaDataContainer()

            for filename in self.audio_files:
                raw_path, raw_filename = os.path.split(filename)
                relative_path = self.absolute_to_relative_path(raw_path)

                meta_data.append(
                    MetaDataItem(
                        {
                            'filename': os.path.join(relative_path, raw_filename),
                            'scene_label': os.path.splitext(os.path.split(filename)[1])[0][:-2],
                        }
                    )
                )

            meta_data.save(
                filename=self.meta_file
            )

            self.load_meta()

        all_folds_found = True
        for fold in self.folds():
            train_filename = self.evaluation_setup_filename(
                setup_part='train',
                fold=fold
            )

            test_filename = self.evaluation_setup_filename(
                setup_part='test',
                fold=fold
            )

            if not os.path.isfile(train_filename):
                all_folds_found = False

            if not os.path.isfile(test_filename):
                all_folds_found = False

        if not all_folds_found:
            Path().makedirs(
                path=self.evaluation_setup_path
            )

            classes = []
            files = []
            for item in self.meta:
                classes.append(item.scene_label)
                files.append(item.filename)

            files = numpy.array(files)

            from sklearn.model_selection import StratifiedShuffleSplit
            sss = StratifiedShuffleSplit(
                n_splits=self.crossvalidation_folds,
                test_size=0.3,
                random_state=0
            )

            fold = 1
            for train_index, test_index in sss.split(X=numpy.zeros(len(classes)), y=classes):
                train_files = files[train_index]
                test_files = files[test_index]
                train_filename = self.evaluation_setup_filename(
                    setup_part='train',
                    fold=fold
                )

                test_filename = self.evaluation_setup_filename(
                    setup_part='test',
                    fold=fold
                )

                eval_filename = self.evaluation_setup_filename(
                    setup_part='evaluate',
                    fold=fold
                )

                # Create meta containers and save them

                # Train
                train_meta = MetaDataContainer(
                    filename=train_filename
                )

                for filename in train_files:
                    train_meta += self.meta_container.filter(
                        filename=filename
                    )

                train_meta.save()

                # Test
                test_meta = MetaDataContainer(
                    filename=test_filename
                )

                for filename in test_files:
                    test_meta.append(
                        MetaDataItem(
                            {
                                'filename': self.absolute_to_relative_path(filename)
                             }
                        )
                    )

                test_meta.save()

                # Evaluate
                eval_meta = MetaDataContainer(
                    filename=eval_filename
                )

                for filename in test_files:
                    eval_meta += self.meta_container.filter(
                        filename=filename
                    )

                eval_meta.save()

                fold += 1

        # Load meta and cross validation
        self.load()

        return self


class DCASE2013_Scenes_EvaluationSet(AcousticSceneDataset):
    """DCASE2013 Acoustic scenes 2013 evaluation dataset

    This dataset was used in DCASE2013 - Task 1, Acoustic scene classification

    """

    def __init__(self,
                 storage_name='DCASE2013-acoustic-scenes-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'DCASE2013-acoustic-scenes-evaluation'

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.
            Default value None

        included_content_types : list of str or str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used. Parameter can be also comma separated string.
            Default value None

        """

        kwargs['included_content_types'] = included_content_types
        kwargs['data_path'] = data_path
        kwargs['storage_name'] = storage_name
        kwargs['dataset_group'] = 'scene'
        kwargs['dataset_meta'] = {
            'authors': 'D. Giannoulis, E. Benetos, D. Stowell, and M. D. Plumbley',
            'title': 'IEEE AASP CASA Challenge - Private Dataset for Scene Classification Task',
            'url': 'https://archive.org/details/dcase2013_scene_classification_testset',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': 'Unknown',
            'microphone_model': 'Soundman OKM II Klassik/studio A3 electret microphone',
        }
        kwargs['crossvalidation_folds'] = 5
        kwargs['package_list'] = [
            {
                'content_type': ['audio', 'documentation'],
                'remote_file': 'https://archive.org/download/dcase2013_scene_classification_testset/scenes_stereo_testset.zip',
                'remote_bytes': 371994727,
                'remote_md5': None,
                'filename': 'scenes_stereo_testset.zip'
            },
            {
                'content_type': ['meta'],
                'remote_file': 'https://archive.org/download/dcase2013_scene_classification_testset/dcase2013_task1_filenamekey.csv',
                'remote_bytes': 8572,
                'remote_md5': None,
                'filename': 'dcase2013_task1_filenamekey.csv'
            }
        ]
        kwargs['audio_paths'] = [
            'audio'
        ]
        super(DCASE2013_Scenes_EvaluationSet, self).__init__(**kwargs)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        Path(os.path.join(self.local_path, 'audio')).create()

        for filename in Path(os.path.join(self.local_path)).file_list(extensions='wav'):
            # Rename files so that they do not overlap with ones in DCASE2013_Scenes_DevelopmentSet
            if not os.path.split(filename)[1].startswith('test_'):
                base, file = os.path.split(filename)
                os.rename(
                    filename,
                    os.path.join(base, 'audio', 'test_' + file)
                )
        self.files = None

        if not self.meta_container.exists():
            meta_data = MetaDataContainer()

            for filename in self.audio_files:
                raw_path, raw_filename = os.path.split(filename)
                relative_path = self.absolute_to_relative_path(raw_path)

                meta_data.append(
                    MetaDataItem(
                        {
                            'filename': os.path.join(relative_path, raw_filename),
                            'scene_label': os.path.splitext(os.path.split(filename)[1])[0][:-2].replace('test_', ''),
                        }
                    )
                )

            meta_data.save(
                filename=self.meta_file
            )

            self.load_meta()

        all_folds_found = True
        for fold in self.folds():
            train_filename = self.evaluation_setup_filename(
                setup_part='train',
                fold=fold
            )

            test_filename = self.evaluation_setup_filename(
                setup_part='test',
                fold=fold
            )

            if not os.path.isfile(train_filename):
                all_folds_found = False

            if not os.path.isfile(test_filename):
                all_folds_found = False

        if not all_folds_found:
            Path().makedirs(
                path=self.evaluation_setup_path
            )

            classes = []
            files = []
            for item in self.meta:
                classes.append(item.scene_label)
                files.append(item.filename)

            files = numpy.array(files)

            from sklearn.model_selection import StratifiedShuffleSplit
            sss = StratifiedShuffleSplit(
                n_splits=self.crossvalidation_folds,
                test_size=0.3,
                random_state=0
            )

            fold = 1
            for train_index, test_index in sss.split(X=numpy.zeros(len(classes)), y=classes):
                train_files = files[train_index]
                test_files = files[test_index]
                train_filename = self.evaluation_setup_filename(
                    setup_part='train',
                    fold=fold
                )

                test_filename = self.evaluation_setup_filename(
                    setup_part='test',
                    fold=fold
                )

                eval_filename = self.evaluation_setup_filename(
                    setup_part='evaluate',
                    fold=fold
                )

                # Create meta containers and save them

                # Train
                train_meta = MetaDataContainer(
                    filename=train_filename
                )

                for filename in train_files:
                    train_meta += self.meta_container.filter(
                        filename=filename
                    )

                train_meta.save()

                # Test
                test_meta = MetaDataContainer(
                    filename=test_filename
                )

                for filename in test_files:
                    test_meta.append(
                        MetaDataItem(
                            {
                                'filename': self.absolute_to_relative_path(filename)
                            }
                        )
                    )

                test_meta.save()

                # Evaluate
                eval_meta = MetaDataContainer(
                    filename=eval_filename
                )

                for filename in test_files:
                    eval_meta += self.meta_container.filter(
                        filename=filename
                    )

                eval_meta.save()

                fold += 1

        # Load meta and cross validation
        self.load()

        return self
