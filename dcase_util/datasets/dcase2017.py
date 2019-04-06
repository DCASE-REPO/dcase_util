# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import os
import sys

from dcase_util.datasets import SoundEventDataset
from dcase_util.containers import MetaDataContainer, MetaDataItem, ListDictContainer, AudioContainer
from dcase_util.utils import Path, is_jupyter


class DCASE2017_Task4tagging_DevelopmentSet(SoundEventDataset):
    """DCASE 2017 Large-scale weakly supervised sound event detection for smart cars

    """

    def __init__(self,
                 storage_name='DCASE2017-task4-development',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'DCASE2017-task4-development'

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
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Benjamin Elizalde, Rohan Badlani, Ankit Shah, Emmanuel Vincent, Bhiksha Raj',
            'title': 'Task 4 Large-scale weakly supervised sound event detection for smart cars',
            'url': 'https://github.com/ankitshah009/Task-4-Large-scale-weakly-supervised-sound-event-detection-for-smart-cars',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': None,
            'microphone_model': None,
            'licence': 'Apache'
        }
        kwargs['crossvalidation_folds'] = 1
        kwargs['default_audio_extension'] = 'flac'
        github_url = 'https://raw.githubusercontent.com/ankitshah009/Task-4-Large-scale-weakly-supervised-sound-event-detection-for-smart-cars/master/'
        kwargs['package_list'] = [
            {
                'content_type': 'meta',
                'remote_file': github_url + 'training_set.csv',
                'remote_bytes': 2368977,
                'remote_md5': 'eba1993f9a10788baf61cee7d968577c',
                'filename': 'training_set.csv',
            },
            {
                'content_type': 'meta',
                'remote_file': github_url + 'testing_set.csv',
                'remote_bytes': 26941,
                'remote_md5': '295d1652a264ec535da3f6a125756ed2',
                'filename': 'testing_set.csv',
            },
            {
                'content_type': 'meta',
                'remote_file': github_url + 'groundtruth_weak_label_training_set.csv',
                'remote_bytes': 2942866,
                'remote_md5': '1a98a76221fa5b5a85aaee9dbf02a2bf',
                'filename': 'groundtruth_weak_label_training_set.csv',
            },
            {
                'content_type': 'meta',
                'remote_file': github_url + 'groundtruth_weak_label_testing_set.csv',
                'remote_bytes': 34199,
                'remote_md5': 'b742b4d6517c82595e09a65d470ff811',
                'filename': 'groundtruth_weak_label_testing_set.csv',
            },
            {
                'content_type': 'documentation',
                'remote_file': github_url + 'APACHE_LICENSE.txt',
                'remote_bytes': 554,
                'remote_md5': '7c99165dc7f440b7270f434683e8c4a1',
                'filename': 'APACHE_LICENSE.txt',
            },
            {
                'content_type': 'documentation',
                'remote_file': github_url + 'README.txt',
                'remote_bytes': 15,
                'remote_md5': '6cb875b80d51f9a26eb05db7f9779011',
                'filename': 'README.txt',
            },
            {
                'content_type': 'documentation',
                'remote_file': github_url + 'sound_event_list_17_classes.txt',
                'remote_bytes': 491,
                'remote_md5': '0312c45c1ab7fc8403dfedaafdc8519f',
                'filename': 'sound_event_list_17_classes.txt',
            },
            {
                'content_type': 'meta',
                'remote_file': github_url + 'groundtruth_strong_label_testing_set.csv',
                'remote_bytes': 37121,
                'remote_md5': 'da6079ac7c196c679b450cefdd0e8700',
                'filename': 'groundtruth_strong_label_testing_set.csv',
            }
        ]
        kwargs['audio_paths'] = ['audio']
        super(DCASE2017_Task4tagging_DevelopmentSet, self).__init__(**kwargs)

    def scene_labels(self):
        labels = ['youtube']
        labels.sort()
        return labels

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        if is_jupyter():
            from tqdm import tqdm_notebook as tqdm
        else:
            from tqdm import tqdm

        # Make sure audio directory exists
        Path().makedirs(path=os.path.join(self.local_path, 'audio'))

        # Make sure evaluation_setup directory exists
        Path().makedirs(path=os.path.join(self.local_path, self.evaluation_setup_folder))

        if 'audio' in self.included_content_types:
            # Collect file ids
            files = []
            files += ListDictContainer(filename=os.path.join(self.local_path, 'testing_set.csv')).load(
                fields=['query_id', 'segment_start', 'segment_end']
            )

            files += ListDictContainer(filename=os.path.join(self.local_path, 'training_set.csv')).load(
                fields=['query_id', 'segment_start', 'segment_end']
            )

            file_progress = tqdm(files,
                                 desc="{0: <25s}".format('Files'),
                                 file=sys.stdout,
                                 leave=False,
                                 disable=self.disable_progress_bar,
                                 ascii=self.use_ascii_progress_bar)

            non_existing_videos = {}

            # Load list of already identified non-accessible videos
            item_access_log_filename = os.path.join(self.local_path, 'item_access_error.log.csv')
            if os.path.isfile(item_access_log_filename):
                for item in ListDictContainer(filename=item_access_log_filename).load(
                    fields=['query_id', 'error']
                ):
                    non_existing_videos[item['query_id']] = item

            # Check that audio files exists
            for file_data in file_progress:
                audio_filename = os.path.join(self.local_path,
                                              'audio',
                                              'Y{query_id}_{segment_start}_{segment_end}.{extension}'.format(
                                                  query_id=file_data['query_id'],
                                                  segment_start=file_data['segment_start'],
                                                  segment_end=file_data['segment_end'],
                                                  extension=self.default_audio_extension
                                              )
                                              )

                # Download segment if it does not exists
                if not os.path.isfile(audio_filename) and file_data['query_id'] not in non_existing_videos:
                    try:
                        AudioContainer().load_from_youtube(
                            query_id=file_data['query_id'],
                            start=file_data['segment_start'],
                            stop=file_data['segment_end']
                        ).save(filename=audio_filename)

                    except IOError as e:
                        non_existing_videos[file_data['query_id']] = {
                            'error': str(e.message).replace('\n', ' '),
                            'query_id': file_data['query_id']
                        }

            # Save list of non-accessible videos
            ListDictContainer(list(non_existing_videos.values()), filename=item_access_log_filename).save(
                fields=['query_id', 'error']
            )

        # Evaluation setup filenames
        train_filename = self.evaluation_setup_filename(
            setup_part='train',
            fold=1,
            scene_label='youtube',
            file_extension='txt'
        )

        test_filename = self.evaluation_setup_filename(
            setup_part='test',
            fold=1,
            scene_label='youtube',
            file_extension='txt'
        )

        evaluate_filename = self.evaluation_setup_filename(
            setup_part='evaluate',
            fold=1,
            scene_label='youtube',
            file_extension='txt'
        )

        # Check that evaluation setup exists
        evaluation_setup_exists = True
        if not os.path.isfile(train_filename) or not os.path.isfile(test_filename) or not os.path.isfile(evaluate_filename):
            evaluation_setup_exists = False

        if not evaluation_setup_exists:
            # Evaluation setup was not found, generate one
            fold = 1

            train_meta = MetaDataContainer()
            for item in MetaDataContainer().load(os.path.join(self.local_path, 'groundtruth_weak_label_training_set.csv')):
                if not item.filename.endswith(self.default_audio_extension):
                    item.filename = os.path.join(
                        'audio',
                        'Y' + os.path.splitext(item.filename)[0] + '.' + self.default_audio_extension
                    )

                # Set scene label
                item.scene_label = 'youtube'

                # Translate event onset and offset, weak labels
                item.offset -= item.onset
                item.onset -= item.onset

                # Only collect items which exists if audio present
                if 'audio' in self.included_content_types:
                    if os.path.isfile(os.path.join(self.local_path, item.filename)):
                        train_meta.append(item)
                else:
                    train_meta.append(item)

            train_meta.save(filename=self.evaluation_setup_filename(
                setup_part='train',
                fold=fold,
                scene_label='youtube',
                file_extension='txt')
            )

            evaluate_meta = MetaDataContainer()
            for item in MetaDataContainer().load(os.path.join(self.local_path, 'groundtruth_strong_label_testing_set.csv')):
                if not item.filename.endswith(self.default_audio_extension):
                    item.filename = os.path.join('audio', 'Y' + os.path.splitext(item.filename)[
                        0] + '.' + self.default_audio_extension)
                # Set scene label
                item.scene_label = 'youtube'

                # Only collect items which exists
                if 'audio' in self.included_content_types:
                    if os.path.isfile(os.path.join(self.local_path, item.filename)):
                        evaluate_meta.append(item)
                else:
                    evaluate_meta.append(item)

            evaluate_meta.save(filename=self.evaluation_setup_filename(
                setup_part='evaluate',
                fold=fold,
                scene_label='youtube',
                file_extension='txt')
            )

            test_meta = MetaDataContainer()
            for item in evaluate_meta:
                test_meta.append(MetaDataItem({'filename': item.filename}))

            test_meta.save(filename=self.evaluation_setup_filename(
                setup_part='test',
                fold=fold,
                scene_label='youtube',
                file_extension='txt')
            )

            # Load meta and cross validation
            self.load()

        if not self.meta_container.exists():
            fold = 1
            meta_data = MetaDataContainer()
            meta_data += MetaDataContainer().load(self.evaluation_setup_filename(
                setup_part='train',
                fold=fold,
                scene_label='youtube',
                file_extension='txt')
            )

            meta_data += MetaDataContainer().load(self.evaluation_setup_filename(
                setup_part='evaluate',
                fold=fold,
                scene_label='youtube',
                file_extension='txt')
            )
            # Save meta
            meta_data.save(filename=self.meta_file)

            # Load meta and cross validation
            self.load()

        return self


class DCASE2017_Task4tagging_EvaluationSet(DCASE2017_Task4tagging_DevelopmentSet):
    """DCASE 2017 Large-scale weakly supervised sound event detection for smart cars

    """

    def __init__(self,
                 storage_name='DCASE2017-task4-evaluation',
                 data_path=None,
                 included_content_types=None,
                 **kwargs):
        """
        Constructor

        Parameters
        ----------

        storage_name : str
            Name to be used when storing dataset on disk
            Default value 'DCASE2017-task4-evaluation'

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
        kwargs['reference_data_present'] = False
        kwargs['dataset_group'] = 'event'
        kwargs['dataset_meta'] = {
            'authors': 'Benjamin Elizalde, Rohan Badlani, Ankit Shah, Emmanuel Vincent, Bhiksha Raj',
            'title': 'Task 4 Large-scale weakly supervised sound event detection for smart cars',
            'url': 'https://github.com/ankitshah009/Task-4-Large-scale-weakly-supervised-sound-event-detection-for-smart-cars',
            'audio_source': 'Field recording',
            'audio_type': 'Natural',
            'recording_device_model': None,
            'microphone_model': None,
        }
        kwargs['crossvalidation_folds'] = None
        kwargs['default_audio_extension'] = 'wav'
        kwargs['package_list'] = [
            {
                'content_type': ['audio'],
                'remote_file': 'https://dl.dropboxusercontent.com/s/bbgqfd47cudwe9y/DCASE_2017_evaluation_set_audio_files.zip',
                'remote_bytes': 863120639,
                'remote_md5': '676b0b4a956db2445b16d7b13522808b',
                'filename': 'DCASE_2017_evaluation_set_audio_files.zip',
                'package_password': 'DCASE_2017_evaluation_set',
            }
        ]
        kwargs['audio_paths'] = ['']

        super(DCASE2017_Task4tagging_DevelopmentSet, self).__init__(**kwargs)

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        # Make sure evaluation_setup directory exists
        Path().makedirs(path=os.path.join(self.local_path, self.evaluation_setup_folder))

        reference_data_file = os.path.join(self.local_path, 'groundtruth_strong_label_evaluation_set.csv')
        if not self.meta_container.exists() and os.path.exists(reference_data_file):
            # Reference data is present and but meta data is empty
            meta_data = MetaDataContainer()
            ref_data = MetaDataContainer().load(filename=reference_data_file)

            for item in ref_data:
                # Modify audio file path
                item.filename = os.path.join('Y' + os.path.splitext(item.filename)[0] + '.' + self.default_audio_extension)

                # Set scene label
                item.scene_label = 'youtube'

                # Only collect items which exists
                if os.path.isfile(os.path.join(self.local_path, item.filename)):
                    meta_data.append(item)

            # Save meta data
            meta_data.save(filename=self.meta_container.filename)

            # Load meta and cross validation
            self.load()

        test_filename = self.evaluation_setup_filename(
            setup_part='test',
            scene_label='youtube',
            file_extension='txt'
        )

        evaluate_filename = self.evaluation_setup_filename(
            setup_part='evaluate',
            scene_label='youtube',
            file_extension='txt'
        )

        # Check that evaluation setup exists
        evaluation_setup_exists = True
        if not os.path.isfile(test_filename) or not os.path.isfile(evaluate_filename):
            evaluation_setup_exists = False

        if not evaluation_setup_exists:
            if os.path.exists(reference_data_file):
                ref_data = MetaDataContainer().load(filename=reference_data_file)
                evaluate_meta = MetaDataContainer()
                for item in ref_data:
                    # Modify audio file path
                    if not item.filename.endswith(self.default_audio_extension):
                        item.filename = os.path.join('audio', 'Y' + os.path.splitext(item.filename)[0] + '.' + self.default_audio_extension)

                    # Set scene label
                    item.scene_label = 'youtube'

                    self.process_meta_item(
                        item=item,
                        absolute_path=False
                    )

                    evaluate_meta.append(item)

                evaluate_meta.save(filename=self.evaluation_setup_filename(
                    setup_part='evaluate',
                    scene_label='youtube',
                    file_extension='txt')
                )

            audio_files = Path().file_list(path=self.local_path, extensions=self.audio_extensions)

            test_meta = MetaDataContainer()
            for audio_file in audio_files:
                item = MetaDataItem({
                    'filename': os.path.split(audio_file)[1],
                    'scene_label': 'youtube'

                })
                self.process_meta_item(
                    item=item,
                    absolute_path=False
                )

                test_meta.append(item)

            test_meta.save(filename=self.evaluation_setup_filename(
                setup_part='test',
                scene_label='youtube',
                file_extension='txt')
            )

            # Load meta and cross validation
            self.load()

        return self
