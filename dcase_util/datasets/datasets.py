#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems

import logging
import os
import sys
import random
import numpy
import tempfile
from tqdm import tqdm

from dcase_util.containers import DictContainer, ListDictContainer, TextContainer, MetaDataContainer
from dcase_util.files import RemoteFile, RemotePackage, File
from dcase_util.utils import get_byte_string, setup_logging, Path
from dcase_util.utils import get_parameter_hash, get_class_inheritors
from dcase_util.ui import FancyLogger


def dataset_list(data_path='data', group=None):
    """List of datasets available

    Parameters
    ----------
    data_path : str
        Base path for the datasets

    group : str
        Group label for the datasets, currently supported ['scene', 'event', 'audio tagging']

    Returns
    -------
    str
        Multi line string containing dataset table

    """
    line = '  {class_name:<42s} | {group:5s} | {remote_size:6s} | {local_present:6s} | {files:5s} | {scene:6s} | {event:6s} | {tag:4s}\n'
    output = ''
    output += '  Dataset list\n'
    output += line.format(
        class_name='Class Name',
        group='Group',
        remote_size='Remote',
        local_present='Local',
        files='Audio',
        scene='Scenes',
        event='Events',
        tag='Tags'
    )
    output += line.format(
        class_name='-' * 42,
        group='-' * 5,
        remote_size='-' * 6,
        local_present='-' * 6,
        files='-' * 5,
        scene='-' * 6,
        event='-' * 6,
        tag='-' * 4
    )

    def get_empty_row():
        return line.format(
            class_name='',
            group='',
            remote_size='',
            local_present='',
            files='',
            scene='',
            event=''
        )

    def get_row(data):
        file_count = 0
        if data.meta_container.exists():
            file_count = len(data.meta)

        return line.format(
            class_name=data.__class__.__name__,
            group=data.dataset_group,
            remote_size=data.dataset_size_string(),
            local_present=data.dataset_size_on_disk(),
            files=str(file_count) if file_count else '',
            scene=str(data.scene_label_count()) if data.scene_label_count() else '',
            event=str(data.event_label_count()) if data.event_label_count() else '',
            tag=str(data.tag_count()) if data.tag_count() else '',
        )

    if not group or group == 'scene':
        class_list = get_class_inheritors(AcousticSceneDataset)
        class_list.sort(key=lambda x: x.__name__, reverse=False)

        for dataset_class in class_list:
            d = dataset_class(data_path=data_path)
            if d.dataset_group != 'base class':
                output += get_row(d)

    if not group or group == 'event':
        class_list = get_class_inheritors(SoundEventDataset)
        class_list.sort(key=lambda x: x.__name__, reverse=False)

        for dataset_class in class_list:
            d = dataset_class(data_path=data_path)
            if d.dataset_group != 'base class':
                output += get_row(d)

    if not group or group == 'tag':
        class_list = get_class_inheritors(AudioTaggingDataset)
        class_list.sort(key=lambda x: x.__name__, reverse=False)

        for dataset_class in class_list:
            d = dataset_class(data_path=data_path)
            if d.dataset_group != 'base class':
                output += get_row(d)

    return output


def dataset_factory(dataset_class_name, **kwargs):
    """Factory to get correct dataset class based on name

    Parameters
    ----------
    dataset_class_name : str
        Class name

    Raises
    ------
    NameError
        Class does not exists

    Returns
    -------
    Dataset class

    """

    try:
        return eval(dataset_class_name)(**kwargs)

    except NameError:
        message = '{name}: No valid dataset given [{dataset_class_name}]'.format(
            name='dataset_factory',
            dataset_class_name=dataset_class_name
        )
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()

        logger.exception(message)
        raise NameError(message)


class Dataset(object):
    """Dataset base class

    The specific dataset classes are inherited from this class, and only needed methods are reimplemented.

    """

    def __init__(self,
                 name='dataset',
                 storage_name='dataset',
                 data_path=None,

                 show_progress_in_console=True,
                 log_system_progress=True,
                 use_ascii_progress_bar=True,

                 dataset_group='base class',
                 dataset_meta=None,

                 evaluation_setup_folder='evaluation_setup',
                 meta_filename='meta.txt',
                 error_meta_filename='error.txt',
                 filelisthash_filename='filelist.python.hash',
                 filelisthash_exclude_dirs=None,
                 crossvalidation_folds=None,
                 package_list=None,
                 included_content_types=None,
                 audio_paths=None,
                 default_audio_extension='wav',
                 reference_data_present=True,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        name : str
            Dataset name

        storage_name : str
            Name to be used when storing dataset on disk

        data_path : str
            Root path where the dataset is stored. If None, os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')
            is used.

        show_progress_in_console : bool
            Show progress in console.

        log_system_progress : bool
            Show progress in log.

        use_ascii_progress_bar : bool
            Show progress bar using ASCII characters. Use this if your console does not support UTF-8 characters.

        dataset_group : str
            Dataset group label, one of ['scene', 'event', 'tag']

        dataset_meta : dict
            Dictionary containing metadata about the dataset, e.g., collecting device information, dataset authors.

        evaluation_setup_folder : str
            Directory name where evaluation setup files are stores

        meta_filename : str
            Filename to be used for main meta file (contains all files with their reference data) of the dataset.

        error_meta_filename : str
            Filename for the error annotation file.

        filelisthash_filename : str
            Filename for filelist hash file.

        filelisthash_exclude_dirs : str
            Directories to be excluded from filelist hash calculation.

        crossvalidation_folds : int
            Count fo cross-validation folds. Indexing starts from one.

        package_list : list of dict
            Package list, remote files associated to the dataset.

        included_content_types : list of str
            Indicates what content type should be processed. One or multiple from ['all', 'audio', 'meta', 'code',
            'documentation']. If None given, ['all'] is used.

        audio_paths : list of str
            List of paths to include audio material associated to the dataset. If None given, ['audio'] is used.

        default_audio_extension : str
            Default audio extension

        reference_data_present : bool
            Reference data is delivered with the dataset.

        """

        self.disable_progress_bar = not show_progress_in_console
        self.log_system_progress = log_system_progress
        self.use_ascii_progress_bar = use_ascii_progress_bar

        # Dataset name
        self.name = name

        # Dataset group
        self.dataset_group = dataset_group

        # Dataset meta
        if dataset_meta is None:
            dataset_meta = {}
        self.dataset_meta = DictContainer(dataset_meta)

        # Folder name for dataset
        self.storage_name = storage_name

        # Path to the dataset
        if data_path is None:
            data_path = os.path.join(tempfile.gettempdir(), 'dcase_util_datasets')

        self.local_path = os.path.join(data_path, self.storage_name)

        # Evaluation setup folder
        self.evaluation_setup_folder = evaluation_setup_folder

        # Path to the folder containing evaluation setup files
        self.evaluation_setup_path = os.path.join(self.local_path, self.evaluation_setup_folder)

        # Meta data file, csv-format
        self.meta_filename = meta_filename
        self.meta_file = os.path.join(self.local_path, self.meta_filename)

        # Error meta data file, csv-format
        self.error_meta_filename = error_meta_filename

        # Path to error meta data file
        self.error_meta_file = os.path.join(self.local_path, self.error_meta_filename)

        # Hash file to detect removed or added files
        self.filelisthash_filename = filelisthash_filename

        # Dirs to be excluded when calculating filelist hash
        if filelisthash_exclude_dirs is None:
            filelisthash_exclude_dirs = []

        self.filelisthash_exclude_dirs = filelisthash_exclude_dirs

        # Number of evaluation folds
        self.crossvalidation_folds = crossvalidation_folds

        # List containing dataset package items
        # Define this in the inherited dataset specific class.
        # Format:
        # {
        #    'content_type': 'documentation',  # Possible values ['meta', 'documentation', 'audio', 'code', 'features']
        #    'remote_file': 'https://zenodo.org/record/45759/files/TUT-sound-events-2016-development.doc.zip', # URL
        #    'remote_bytes': 70918,            # Size of remote file in bytes
        #    'remote_md5': '33fd26a895530aef607a07b08704eacd',  # MD5 hash of remote file
        #    'filename': 'TUT-sound-events-2016-development.doc.zip' # filename relative to self.local_path always
        # }
        if package_list is None:
            package_list = []
        self.package_list = ListDictContainer(package_list)

        # Expand local filenames to be related to local path
        for item in self.package_list:
            item['filename'] = os.path.join(self.local_path, item['filename'])

        # What content type should be processed. Use this for example to access only the meta data, and exclude usually
        # large and time consuming audio material downloading. Leave to "all" to include all content types.
        if included_content_types is None:
            included_content_types = ['all']

        self.included_content_types = included_content_types

        # Inject all included content types, there might be packages containing multiple content types.
        if 'all' not in self.included_content_types:
            for package_data in self.package_list:
                package_item = RemoteFile(**package_data)
                if self.included_content_types is None or package_item.is_content_type(
                        content_type=self.included_content_types
                ):
                    self.included_content_types = list(set().union(
                        package_item.content_type, self.included_content_types)
                    )

        # List of directories to contain the audio material
        if audio_paths is None:
            audio_paths = ['audio']
        self.audio_paths = audio_paths

        # Expand local filenames to be related to local path
        for path_id, path in enumerate(self.audio_paths):
            self.audio_paths[path_id] = os.path.join(self.local_path, path)

        # List of audio files
        self.files = None

        # Recognized audio extensions
        self.audio_extensions = ['wav', 'flac']

        self.default_audio_extension = default_audio_extension

        # Reference data presence flag, by default dataset should have reference data present.
        # However, some evaluation dataset might not have
        self.reference_data_present = reference_data_present

        # Initialize meta data container
        self.meta_container = MetaDataContainer()

        # List of audio error meta data dict
        self.error_meta_data = None

        # Cross-validation data
        self.crossvalidation_data = DictContainer({
            'train': {},
            'test': {},
            'evaluate': {},
        })

        # Training meta data for folds
        self.crossvalidation_data_train = {}

        # Testing meta data for folds
        self.crossvalidation_data_test = {}

        # Evaluation meta data for folds
        self.crossvalidation_data_eval = {}

        # Load meta and cross-validation data in
        self.load()

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    def load(self):
        """Load dataset meta data and cross-validation sets into the container."""
        self.load_meta()
        self.load_crossvalidation_data()

    def load_meta(self):
        """Load meta data into the container."""
        # Initialize meta container
        self.meta_container = MetaDataContainer(filename=os.path.join(self.local_path, self.meta_filename))

        # Load from disk only if file exists
        if self.meta_container.exists():
            # Load meta data
            self.meta_container.load()

            # Mark reference data being present
            self.reference_data_present = True

        return self

    def load_crossvalidation_data(self):
        """Load cross-validation into the container.

        Returns
        -------
        self

        """

        # Reset cross validation data and insert 'all_data'
        self.crossvalidation_data = DictContainer({
            'train': {
                'all_data': self.meta_container
            },
            'test': {
                'all_data': self.meta_container
            },
            'evaluate': {
                'all_data': self.meta_container
            },
        })

        for crossvalidation_set in list(self.crossvalidation_data.keys()):
            for item in self.crossvalidation_data[crossvalidation_set]['all_data']:
                self.process_meta_item(item=item)

        # Load cross validation folds
        for fold in self.folds():
            # Get filenames
            train_filename = self.evaluation_setup_filename(setup_part='train', fold=fold)
            test_filename = self.evaluation_setup_filename(setup_part='test', fold=fold)
            evaluate_filename = self.evaluation_setup_filename(setup_part='evaluate', fold=fold)

            if os.path.isfile(train_filename):
                # Training data for fold exists, load and process it
                self.crossvalidation_data['train'][fold] = MetaDataContainer(filename=train_filename).load()

                # Process items
                for item in self.crossvalidation_data['train'][fold]:
                    self.process_meta_item(item=item)

            else:
                # Initialize data
                self.crossvalidation_data['train'][fold] = MetaDataContainer()

            if os.path.isfile(test_filename):
                # Testing data for fold exists, load and process it
                self.crossvalidation_data['test'][fold] = MetaDataContainer(filename=test_filename).load()

                # Process items
                for item in self.crossvalidation_data['test'][fold]:
                    self.process_meta_item(item=item)

            else:
                # Initialize data
                self.crossvalidation_data['test'][fold] = MetaDataContainer()

            if os.path.isfile(evaluate_filename):
                # Evaluation data for fold exists, load and process it
                self.crossvalidation_data['evaluate'][fold] = MetaDataContainer(filename=evaluate_filename).load()

                # Process items
                for item in self.crossvalidation_data['evaluate'][fold]:
                    self.process_meta_item(item=item)

            else:
                # Initialize data
                self.crossvalidation_data['evaluate'][fold] = MetaDataContainer()

        return self

    def __getitem__(self, i):
        """Getting meta data item

        Parameters
        ----------
        i : int
            item id

        Returns
        -------
        meta_data : dict
            Meta data item

        """

        if i < len(self.meta_container):
            return self.meta_container[i]
        else:
            return None

    def __iter__(self):
        """Iterator for meta data items
        """

        i = 0
        meta = self[i]

        # yield window while it's valid
        while meta is not None:
            yield meta
            # get next item
            i += 1
            meta = self[i]

    def initialize(self):
        """Initialize the dataset, download, extract files and prepare the dataset for the usage.

        Returns
        -------
        self

        """

        # Create the dataset path if does not exist
        Path().makedirs(path=self.local_path)

        # Check file changes
        if not self.check_filelist():
            # Download packages
            self.download_packages()

            # Extract content from packages
            self.extract_packages()

            # Load meta data in
            self.load()

            # Prepare meta data for the dataset class.
            self.prepare()

            # Save new filelist hash to monitor change in the dataset.
            self._save_filelist_hash()

        return self

    def show(self):
        """Print dataset information."""
        DictContainer(self.dataset_meta).show()
        self.meta_container.show(show_data=False, show_stats=True)

    def log(self):
        """Log dataset information."""
        DictContainer(self.dataset_meta).log()
        self.meta_container.log(show_data=False, show_stats=True)

    @property
    def audio_files(self):
        """Get all audio files in the dataset

        Parameters
        ----------

        Returns
        -------
        list
            File list with absolute paths

        """

        if self.files is None:
            self.files = []
            for path in self.audio_paths:
                if path and os.path.exists(path):
                    dir_list = os.listdir(path)
                    for f in dir_list:
                        file_name, file_extension = os.path.splitext(f)
                        if file_extension[1:] in self.audio_extensions:
                            if os.path.abspath(os.path.join(path, f)) not in self.files:
                                self.files.append(os.path.abspath(os.path.join(path, f)))
            self.files.sort()
        return self.files

    @property
    def audio_file_count(self):
        """Get number of audio files in dataset

        Parameters
        ----------

        Returns
        -------
        int
            Number of audio files

        """

        return len(self.audio_files)

    @property
    def meta(self):
        """Get meta data for dataset. If not already read from disk, data is read and returned.

        Raises
        ------
        IOError
            meta file not found.

        Returns
        -------
        list
            List containing meta data as dict.

        """

        if self.meta_container.empty():
            if self.meta_container.exists():
                self.meta_container.load()
            else:
                message = '{name}: Meta file not found [{filename}]'.format(
                    name=self.__class__.__name__,
                    filename=self.meta_container.filename
                )

                self.logger.exception(message)
                raise IOError(message)

        return self.meta_container

    @property
    def meta_count(self):
        """Number of meta data items.

        Returns
        -------
        int
            Meta data item count

        """

        return len(self.meta_container)

    @property
    def error_meta(self):
        """Get audio error meta data for dataset. If not already read from disk, data is read and returned.

        Raises
        ------
        IOError:
            audio error meta file not found.

        Returns
        -------
        MetaDataContainer
            List containing audio error meta data as dict.

        """

        if self.error_meta_data is None:
            self.error_meta_data = MetaDataContainer(filename=self.error_meta_file)
            if self.error_meta_data.exists():
                self.error_meta_data.load()
            else:
                message = '{name}: Error meta file not found [{filename}]'.format(name=self.__class__.__name__,
                                                                                  filename=self.error_meta_file)
                self.logger.exception(message)
                raise IOError(message)

        return self.error_meta_data

    @property
    def error_meta_count(self):
        """Number of error meta data items.

        Returns
        -------
        int
            Meta data item count

        """

        return len(self.error_meta)

    @property
    def fold_count(self):
        """Number of fold in the evaluation setup.

        Returns
        -------
        int
            Number of folds

        """

        return self.crossvalidation_folds

    def scene_labels(self):
        """List of unique scene labels in the meta data.

        Returns
        -------
        list
            List of scene labels in alphabetical order.

        """

        return self.meta_container.unique_scene_labels

    def scene_label_count(self):
        """Number of unique scene labels in the meta data.

        Returns
        -------
        int
            Number of unique scene labels.

        """

        return self.meta_container.scene_label_count

    def event_labels(self, **kwargs):
        """List of unique event labels in the meta data.

        Returns
        -------
        list
            List of event labels in alphabetical order.

        """

        return self.meta_container.unique_event_labels

    def event_label_count(self, **kwargs):
        """Number of unique event labels in the meta data.

        Returns
        -------
        int
            Number of unique event labels

        """

        return self.meta_container.event_label_count

    def tags(self):
        """List of unique audio tags in the meta data.

        Returns
        -------
        list
            List of audio tags in alphabetical order.

        """

        return self.meta_container.unique_tags

    def tag_count(self):
        """Number of unique audio tags in the meta data.

        Returns
        -------
        int
            Number of unique audio tags

        """

        return len(self.tags())

    def download_packages(self):
        """Download dataset packages over the internet to the local path

        Raises
        ------
        IOError
            Download failed.

        Returns
        -------
        self

        """

        # Create the dataset path if does not exist
        Path().makedirs(path=self.local_path)

        item_progress = tqdm(self.package_list,
                             desc="{0: <25s}".format('Download packages'),
                             file=sys.stdout,
                             leave=False,
                             disable=self.disable_progress_bar,
                             ascii=self.use_ascii_progress_bar)

        for item in item_progress:
            remote_file = RemoteFile(**item)
            if self.included_content_types is None or remote_file.is_content_type(
                    content_type=self.included_content_types
            ):
                remote_file.download()

        return self

    def extract_packages(self):
        """Extract the dataset packages

        Raises
        ------
        IOError
            Local package was not found.

        Returns
        -------
        self


        """

        item_progress = tqdm(self.package_list,
                             desc="{0: <25s}".format('Extract packages'),
                             file=sys.stdout,
                             leave=False,
                             disable=self.disable_progress_bar,
                             ascii=self.use_ascii_progress_bar)

        for item_id, item in enumerate(item_progress):
            if File().is_package(filename=item['filename']):
                # Process only files which are packages
                remote_package = RemotePackage(**item)

                if self.included_content_types is None or remote_package.is_content_type(
                        content_type=self.included_content_types
                ):
                    if remote_package.local_exists():
                        remote_package.extract()

                    else:
                        # Local file not present
                        message = '{name}: Local package does not exists [{filename}]'.format(
                            name=self.__class__.__name__,
                            filename=remote_package.filename,
                        )
                        self.logger.exception(message)
                        raise IOError(message)

        return self

    def prepare(self):
        """Prepare dataset for the usage.

        Returns
        -------
        self

        """

        return self

    def check_filelist(self):
        """Generates hash from file list and check does it matches with one saved in filelist.hash.
        If some files have been deleted or added, checking will result False.

        Returns
        -------
        bool
            Result

        """

        if os.path.isfile(os.path.join(self.local_path, self.filelisthash_filename)):
            old_hash_value = TextContainer(filename=os.path.join(self.local_path, self.filelisthash_filename)).load()[0]

            file_list = self._get_filelist(exclude_dirs=self.filelisthash_exclude_dirs)
            new_hash_value = get_parameter_hash(file_list)

            if self.included_content_types:
                new_hash_value += ';'+','.join(self.included_content_types)

            if old_hash_value != new_hash_value:
                return False

            else:
                return True

        else:
            return False

    def process_meta_item(self, item, absolute_path=True, **kwargs):
        """Process single meta data item

        Parameters
        ----------
        item :  MetaDataItem
            Meta data item

        absolute_path : bool
            Convert file paths to be absolute

        """

        if absolute_path:
            item.filename = self.relative_to_absolute_path(item.filename)

    def evaluation_setup_filename(self, setup_part='train', fold=None, scene_label=None, file_extension='txt'):
        """Evaluation setup filename generation.

        Parameters
        ----------
        setup_part :  str
            Setup part 'train', 'test', 'evaluate'

        fold : int
            Fold number
        scene_label : str
            Scene label

        file_extension : str
            File extension

        Raises
        ------
        ValueError
            Unknown setup part.

        Returns
        -------
        str
            Filename with full path.

        """

        if fold == 'all_data':
            fold = None

        parts = []
        if scene_label:
            parts.append(scene_label)

        if fold:
            parts.append('fold' + str(fold))

        if setup_part == 'train':
            parts.append('train')

        elif setup_part == 'test':
            parts.append('test')

        elif setup_part == 'evaluate':
            parts.append('evaluate')

        else:
            message = '{name}: Unknown setup_part [{setup_part}]'.format(
                name=self.__class__.__name__,
                setup_part=setup_part
            )

            self.logger.exception(message)
            raise ValueError(message)

        return os.path.join(self.evaluation_setup_path, '_'.join(parts) + '.' + file_extension)

    def train(self, fold=None, **kwargs):
        """List of training items.

        Parameters
        ----------
        fold : int [scalar]
            Fold id, if None all meta data is returned.

        Returns
        -------
        MetaDataContainer
            List containing all meta data assigned to training set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        return self.crossvalidation_data['train'][fold]

    def test(self, fold=None, **kwargs):
        """List of testing items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        Returns
        -------
        MetaDataContainer
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        return self.crossvalidation_data['test'][fold]

    def eval(self, fold=None, **kwargs):
        """List of evaluation items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        Returns
        -------
        MetaDataContainer
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        return self.crossvalidation_data['evaluate'][fold]

    def train_files(self, fold=None, **kwargs):
        """List of training files.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        Returns
        -------
        list of str
            List containing all files assigned to training set for given fold.

        """

        return self.train(fold=fold).unique_files

    def test_files(self, fold=None, **kwargs):
        """List of testing files.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        Returns
        -------
        list of str
            List containing all files assigned to testing set for given fold.

        """

        return self.test(fold=fold).unique_files

    def eval_files(self, fold=None, **kwargs):
        """List of evaluation files.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        Returns
        -------
        list of str
            List containing all files assigned to testing set for given fold.

        """

        return self.eval(fold=fold).unique_files

    def validation_split(self,
                         fold=None, split_type='balanced', validation_amount=None,
                         seed=0, verbose=False, scene_label=None, iterations=100,
                         **kwargs):
        """List of validation files. Validation files are always subset of training files.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        split_type : str
            Split type [dataset, random, balanced]

        validation_amount : float
            Amount of training files to be assigned for validation

        seed : int
            Randomization seed

        verbose : bool
            Show information about the validation set.

        scene_label : str
            Scene label of the validation set. If None, all training material used.

        iterations : int
            Randomization iterations done when finding balanced set before selecting best matched set.

        Returns
        -------
        list of str
            List containing all files assigned to training set for given fold.

        list of str
            List containing all files assigned to validation set for given fold.

        """

        kwargs.update({
            'fold': fold,
            'validation_amount': validation_amount,
            'seed': seed,
            'verbose': verbose,
            'scene_label': scene_label,
            'iterations': iterations,
        })

        if split_type == 'dataset':
            validation_files = self.validation_files_dataset(**kwargs)

        elif split_type == 'random':
            validation_files = self.validation_files_random(**kwargs)

        elif split_type == 'balanced':
            validation_files = self.validation_files_balanced(**kwargs)

        else:
            message = '{name}: Unknown split type [{split_type}]'.format(
                name=self.__class__.__name__,
                split_type=split_type
            )

            self.logger.exception(message)
            raise IOError(message)

        training_files = sorted(list(set(self.train(fold=fold).unique_files) - set(validation_files)))

        return training_files, validation_files

    def validation_files_dataset(self, fold=None, verbose=False, **kwargs):
        """List of validation files delivered by the dataset."""

        message = '{name}: Dataset does not have fixed validation sets, use validation set generation to get sets'.format(
            name=self.__class__.__name__,
        )

        self.logger.exception(message)
        raise ValueError(message)

    def validation_files_random(self, fold=None, validation_amount=0.3, seed=0, verbose=False, **kwargs):
        """List of validation files selected randomly from the training material.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        validation_amount : float
            Amount of training material to be assigned for validation.

        seed : int
            Randomization seed

        verbose : bool
            Show information about the validation set.

        Returns
        -------
        list of str
            List containing all files assigned for validation

        """

        random.seed(seed)

        training_meta = self.train(fold=fold)
        training_files = training_meta.unique_files
        random.shuffle(training_files, random.random)

        validation_split_index = int(numpy.ceil(validation_amount * len(training_files)))
        validation_files = training_files[0:validation_split_index]

        if verbose:
            validation_meta = self.train(fold=fold).filter(file_list=validation_files)

            validation_amounts = numpy.zeros((len(self.scene_labels())+1, 3))
            for scene_id, scene_label in enumerate(self.scene_labels()):
                validation_scene_meta = validation_meta.filter(scene_label=scene_label)
                validation_amounts[scene_id, 0] = len(validation_scene_meta.unique_identifiers)
                validation_amounts[scene_id, 1] = len(validation_scene_meta.unique_files)
                validation_amounts[scene_id, 2] = len(validation_scene_meta.unique_files) / float(len(training_meta.filter(scene_label=scene_label).unique_files)) * 100
            validation_amounts[-1, 0] = numpy.sum(validation_amounts[0:-1, 0])
            validation_amounts[-1, 1] = numpy.sum(validation_amounts[0:-1, 1])
            validation_amounts[-1, 2] = numpy.mean(validation_amounts[0:-1, 2])

            labels = self.scene_labels()
            labels.append('Overall')

            FancyLogger().sub_header('Validation set for fold [{fold}] / random'.format(fold=fold), indent=2)
            FancyLogger().table(
                cell_data=[labels] + validation_amounts.T.tolist(),
                column_headers=['Scene', 'Identifiers', 'Files', 'Amount (%)'],
                column_types=['str20', 'int', 'int', 'float1'],
                column_separators=[0, 1],
                row_separators=[len(labels) - 1],
                indent=2
            )

        return validation_files

    def validation_files_balanced(self, fold=None, validation_amount=0.3, seed=0, verbose=False, **kwargs):
        """List of validation files randomly selecting while maintaining data balance."""
        message = '{name}: Balanced validation set generation has not been implemented for dataset class.'.format(
            name=self.__class__.__name__,
        )

        self.logger.exception(message)
        raise ValueError(message)

    def folds(self, mode='folds'):
        """List of fold ids

        Parameters
        ----------
        mode : str {'folds','full'}
            Fold setup type, possible values are 'folds' and 'full'. In 'full' mode fold number is set 0 and
            all data is used for training.

        Returns
        -------
        list of int
            Fold ids

        """

        if mode == 'folds':
            if self.crossvalidation_folds is not None:
                return list(range(1, self.crossvalidation_folds+1))
            else:
                return ['all_data']

        elif mode == 'full':
            return ['all_data']

    def file_meta(self, filename):
        """Meta data for given file

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        list of dict
            List containing all meta data related to given file.

        """

        # Try first with raw filename
        file_meta = self.meta_container.filter(
            filename=filename
        )

        if not file_meta:
            # Try with absolute filename
            file_meta = self.meta_container.filter(
                filename=self.absolute_to_relative(filename)
            )

        if not file_meta:
            # Try with relative filename
            file_meta = self.meta_container.filter(
                filename=self.relative_to_absolute_path(filename)
            )

        return file_meta

    def file_error_meta(self, filename):
        """Error meta data for given file

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        list of dict
            List containing all error meta data related to given file.

        """
        error_meta = self.error_meta.filter(filename=filename)

        if not error_meta:
            error_meta = self.error_meta.filter(
                filename=self.absolute_to_relative(filename)
            )

        if not error_meta:
            error_meta = self.error_meta.filter(
                filename=self.relative_to_absolute_path(filename)
            )

        return error_meta

    def file_features(self, filename):
        """Pre-calculated acoustic features for given file

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        numpy.ndarray
            Matrix containing acoustic features

        """
        pass

    def relative_to_absolute_path(self, path):
        """Converts relative path into absolute path.

        Parameters
        ----------
        path : str
            Relative path

        Returns
        -------
        str
            Absolute path

        """

        return os.path.abspath(os.path.expanduser(os.path.join(self.local_path, path)))

    def absolute_to_relative(self, path):
        """Converts absolute path into relative path.

        Parameters
        ----------
        path : str
            Absolute path

        Returns
        -------
        str
            Relative path

        """

        if path.startswith(os.path.abspath(self.local_path)):
            return os.path.relpath(path, self.local_path)

        else:
            return path

    def dataset_bytes(self):
        """Total download size of the dataset in bytes.

        Returns
        -------
        int
            Total bytes

        """

        total_bytes = 0
        for item_id, item in enumerate(self.package_list):
            remote_package = RemoteFile(**item)

            if remote_package.local_exists():
                total_bytes += remote_package.local_bytes

            else:
                total_bytes += remote_package.remote_bytes

        return total_bytes

    def dataset_size_string(self):
        """Total download size of the dataset in a string.

        Returns
        -------
        str
            Total size

        """

        return get_byte_string(self.dataset_bytes(), show_bytes=False)

    def dataset_size_on_disk(self):
        """Total size of the dataset currently stored locally.

        Returns
        -------
        str
            Total size

        """

        total_size = 0
        for dir_path, dir_names, filenames in os.walk(self.local_path):
            for f in filenames:
                fp = os.path.join(dir_path, f)
                total_size += os.path.getsize(fp)

        return get_byte_string(total_size, show_bytes=False)

    def _get_filelist(self, exclude_dirs=None):
        """List of files under local_path

        Parameters
        ----------
        exclude_dirs : list of str
            List of directories to be excluded

        Returns
        -------
        list of str
            File list

        """

        if exclude_dirs is None:
            exclude_dirs = []

        filelist = []
        for path, sub_directory, files in os.walk(self.local_path):
            for name in files:
                if os.path.splitext(name)[1] != os.path.splitext(self.filelisthash_filename)[1] and os.path.split(path)[1] not in exclude_dirs:
                    filelist.append(os.path.join(path, name))

        return sorted(filelist)

    def _save_filelist_hash(self):
        """Generates file list hash, and saves it as filelist.hash under local_path.

        Parameters
        ----------

        Returns
        -------
        None

        """

        filelist = self._get_filelist()

        hash_value = get_parameter_hash(filelist)
        if self.included_content_types:
            hash_value += ';'+','.join(self.included_content_types)

        TextContainer([hash_value]).save(
            filename=os.path.join(self.local_path, self.filelisthash_filename)
        )


class AcousticSceneDataset(Dataset):
    def __init__(self, *args, **kwargs):
        super(AcousticSceneDataset, self).__init__(*args, **kwargs)

    def validation_files_balanced(self,
                                  fold=None, validation_amount=0.3, seed=0, verbose=False, iterations=100,
                                  **kwargs):
        """List of validation files randomly selecting while maintaining data balance.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        validation_amount : float
            Amount of training material to be assigned for validation.

        seed : int
            Randomization seed

        verbose : bool
            Show information about the validation set.

        iterations : int
            How many randomization iterations will be done before selecting best matched.

        Returns
        -------
        list of str
            List containing all files assigned for validation

        """

        random.seed(seed)
        training_meta = self.train(fold=fold)

        # Check do we have location/source identifier present
        identifier_present = False
        for item in training_meta:
            if item.identifier:
                identifier_present = True
                break

        training_files = []
        validation_files = []
        validation_amounts = numpy.zeros((len(self.scene_labels())+1, 3))

        if identifier_present:
            # Do the balance based on scene class and identifier
            for scene_id, scene_label in enumerate(self.scene_labels()):
                scene_meta = training_meta.filter(scene_label=scene_label)

                data = {}
                for identifier in scene_meta.unique_identifiers:
                    data[identifier] = scene_meta.filter(identifier=identifier).unique_files

                current_scene_validation_amount = []
                sets_candidates = []

                iteration_progress = tqdm(
                    range(0, iterations),
                    desc="{0: <25s}".format('Generate validation split candidates'),
                    file=sys.stdout,
                    leave=False,
                    disable=self.disable_progress_bar,
                    ascii=self.use_ascii_progress_bar
                )

                for i in iteration_progress:
                    current_locations = list(data.keys())
                    random.shuffle(current_locations, random.random)
                    validation_split_index = int(numpy.ceil(validation_amount * len(data)))
                    current_validation_identifiers = current_locations[0:validation_split_index]
                    current_training_identifiers = current_locations[validation_split_index:]

                    # Collect validation files
                    current_validation_files = []
                    for identifier in current_validation_identifiers:
                        current_validation_files += data[identifier]

                    # Collect training files
                    current_training_files = []
                    for identifier in current_training_identifiers:
                        current_training_files += data[identifier]

                    current_scene_validation_amount.append(
                        len(current_validation_files) / float(len(current_validation_files) + len(current_training_files))
                    )

                    sets_candidates.append({
                        'validation': current_validation_files,
                        'training': current_training_files,
                    })

                best_set_id = numpy.argmin(numpy.abs(numpy.array(current_scene_validation_amount) - validation_amount))
                validation_files += sets_candidates[best_set_id]['validation']
                training_files += sets_candidates[best_set_id]['training']
                validation_amounts[scene_id, 0] = len(scene_meta.unique_identifiers)
                validation_amounts[scene_id, 1] = len(scene_meta.unique_files)
                validation_amounts[scene_id, 2] = current_scene_validation_amount[best_set_id] * 100

        else:
            # Do the balance based on scene class only
            for scene_id, scene_label in enumerate(self.scene_labels()):
                scene_files = training_meta.filter(scene_label=scene_label).unique_files

                random.shuffle(scene_files, random.random)
                validation_split_index = int(numpy.ceil(validation_amount * len(scene_files)))
                current_validation_files = scene_files[0:validation_split_index]
                current_training_files = scene_files[validation_split_index:]

                validation_files += current_validation_files
                training_files += current_training_files
                validation_amounts[scene_id, 1] = len(scene_files)
                validation_amounts[scene_id, 2] = len(current_validation_files) / float(len(current_validation_files) + len(current_training_files)) * 100

        if verbose:
            validation_amounts[-1, 0] = numpy.sum(validation_amounts[0:-1, 0])
            validation_amounts[-1, 1] = numpy.sum(validation_amounts[0:-1, 1])
            validation_amounts[-1, 2] = numpy.mean(validation_amounts[0:-1, 2])

            labels = self.scene_labels()
            labels.append('Overall')
            logger = FancyLogger()
            logger.sub_header('Validation set for fold [{fold}] / balanced'.format(fold=fold), indent=2)
            logger.table(
                cell_data=[labels] + validation_amounts.T.tolist(),
                column_headers=['Scene', 'Identifiers', 'Files', 'Amount (%)'],
                column_types=['str20', 'int', 'int', 'float1'],
                column_separators=[0, 1],
                row_separators=[len(labels)-1],
                indent=2
            )

        return validation_files


class SoundEventDataset(Dataset):
    def __init__(self, *args, **kwargs):
        super(SoundEventDataset, self).__init__(*args, **kwargs)

    def load_crossvalidation_data(self):
        """Load cross-validation into the container.

        Returns
        -------
        self

        """

        # Reset cross validation data and insert 'all_data'
        self.crossvalidation_data = DictContainer({
            'train': {
                'all_data': self.meta_container
            },
            'test': {
                'all_data': self.meta_container
            },
            'evaluate': {
                'all_data': self.meta_container
            },
        })

        for crossvalidation_set in list(self.crossvalidation_data.keys()):
            for item in self.crossvalidation_data[crossvalidation_set]['all_data']:
                self.process_meta_item(item=item)

        # Load cross validation folds
        for fold in self.folds():
            # Initialize data
            self.crossvalidation_data['train'][fold] = MetaDataContainer()
            self.crossvalidation_data['test'][fold] = MetaDataContainer()
            self.crossvalidation_data['evaluate'][fold] = MetaDataContainer()

            for scene_label in self.scene_labels():
                # Get filenames
                train_filename = self.evaluation_setup_filename(
                    setup_part='train',
                    fold=fold,
                    scene_label=scene_label
                )

                test_filename = self.evaluation_setup_filename(
                    setup_part='test',
                    fold=fold,
                    scene_label=scene_label
                )

                evaluate_filename = self.evaluation_setup_filename(
                    setup_part='evaluate',
                    fold=fold,
                    scene_label=scene_label
                )

                if os.path.isfile(train_filename):
                    # Training data for fold exists, load and process it
                    self.crossvalidation_data['train'][fold] += MetaDataContainer(filename=train_filename).load()

                if os.path.isfile(test_filename):
                    # Testing data for fold exists, load and process it
                    self.crossvalidation_data['test'][fold] += MetaDataContainer(filename=test_filename).load()

                if os.path.isfile(evaluate_filename):
                    # Evaluation data for fold exists, load and process it
                    self.crossvalidation_data['evaluate'][fold] += MetaDataContainer(filename=evaluate_filename).load()

            # Process items
            for item in self.crossvalidation_data['train'][fold]:
                self.process_meta_item(item=item)

            for item in self.crossvalidation_data['test'][fold]:
                self.process_meta_item(item=item)

            for item in self.crossvalidation_data['evaluate'][fold]:
                self.process_meta_item(item=item)

        return self

    def event_label_count(self, scene_label=None):
        """Number of unique scene labels in the meta data.

        Parameters
        ----------
        scene_label : str
            Scene label

        Returns
        -------
        int
            Number of unique scene labels.

        """

        return len(self.event_labels(scene_label=scene_label))

    def event_labels(self, scene_label=None):
        """List of unique event labels in the meta data.

        Parameters
        ----------
        scene_label : str
            Scene label

        Returns
        -------
        list of str
            List of event labels in alphabetical order.

        """

        if scene_label is not None:
            labels = self.meta_container.filter(scene_label=scene_label).unique_event_labels
        else:
            labels = self.meta_container.unique_event_labels

        labels.sort()
        return labels

    def train(self, fold=None, scene_label=None, event_label=None, **kwargs):
        """List of training items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        scene_label : str
            Scene label
        event_label : str
            Event label

        Returns
        -------
        list of dict
            List containing all meta data assigned to training set for given fold.

        """
        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['train'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        return data

    def test(self, fold=None, scene_label=None, event_label=None, **kwargs):
        """List of testing items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        scene_label : str
            Scene label

        event_label : str
            Event label

        Returns
        -------
        list of dict
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['test'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        return data

    def eval(self, fold=None, scene_label=None, event_label=None, **kwargs):
        """List of evaluation items.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        scene_label : str
            Scene label

        event_label : str
            Event label

        Returns
        -------
        list of dict
            List containing all meta data assigned to testing set for given fold.

        """

        if fold is None or fold == 0:
            fold = 'all_data'

        data = self.crossvalidation_data['evaluate'][fold]

        if scene_label:
            data = data.filter(scene_label=scene_label)

        if event_label:
            data = data.filter(event_label=event_label)

        return data

    def train_files(self, fold=None, scene_label=None, event_label=None, **kwargs):
        """List of training files.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        scene_label : str
            Scene label

        event_label : str
            Event label

        Returns
        -------
        list of str
            List containing all files assigned to training set for given fold.

        """

        return self.train(
            fold=fold,
            scene_label=scene_label,
            event_label=event_label
        ).unique_files

    def test_files(self, fold=None, scene_label=None, event_label=None, **kwargs):
        """List of testing files.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        scene_label : str
            Scene label

        event_label : str
            Event label

        Returns
        -------
        list of str
            List containing all files assigned to testing set for given fold.

        """

        return self.test(
            fold=fold,
            scene_label=scene_label,
            event_label=event_label
        ).unique_files

    def eval_files(self, fold=None, scene_label=None, event_label=None, **kwargs):
        """List of evaluation files.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        scene_label : str
            Scene label

        event_label : str
            Event label

        Returns
        -------
        list of str
            List containing all files assigned to testing set for given fold.

        """

        return self.eval(
            fold=fold,
            scene_label=scene_label,
            event_label=event_label
        ).unique_files

    def validation_files_random(self,
                                fold=None, validation_amount=0.3, seed=0, verbose=False, scene_label=None,
                                **kwargs):
        """List of validation files selected randomly from the training material.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        validation_amount : float
            Amount of training material to be assigned for validation.

        seed : int
            Randomization seed

        verbose : bool
            Show information about the validation set.

        scene_label : str
            Scene label of the validation set. If None, all training material used.

        Returns
        -------
        list of str
            List containing all files assigned for validation

        """

        random.seed(seed)
        training_meta = self.train(fold=fold, scene_label=scene_label)

        if scene_label:
            scene_labels = [scene_label]
        else:
            scene_labels = self.scene_labels()

        training_files = training_meta.unique_files
        random.shuffle(training_files, random.random)

        validation_split_index = int(numpy.ceil(validation_amount * len(training_files)))
        validation_files = training_files[0:validation_split_index]

        if verbose:
            logger = FancyLogger()
            logger.sub_header('Validation set for fold [{fold}] / random'.format(fold=fold), indent=2)
            for scene_id, scene_label in enumerate(scene_labels):
                all_stats = training_meta.filter(scene_label=scene_label).event_stat_counts()
                validation_stats = training_meta.filter(scene_label=scene_label, file_list=validation_files).event_stat_counts()
                training_files = sorted(list(set(self.train(fold=fold).unique_files) - set(validation_files)))
                training_stats = training_meta.filter(scene_label=scene_label, file_list=training_files).event_stat_counts()

                cell_data = numpy.zeros((len(list(all_stats.keys())) + 1, 4))
                for event_id, event_label in enumerate(list(all_stats.keys())):
                    cell_data[event_id, 0] = all_stats[event_label]
                    if event_label in training_stats:
                        cell_data[event_id, 1] = training_stats[event_label]

                    if event_label in validation_stats:
                        cell_data[event_id, 2] = validation_stats[event_label]

                    cell_data[event_id, 3] = cell_data[event_id, 2] / float(cell_data[event_id, 0]) * 100

                cell_data[-1, 0] = numpy.sum(list(all_stats.values()))
                cell_data[-1, 1] = numpy.sum(list(training_stats.values()))
                cell_data[-1, 2] = numpy.sum(list(validation_stats.values()))
                cell_data[-1, 3] = cell_data[-1, 2] / float(cell_data[-1, 0]) * 100

                labels = list(all_stats.keys())
                labels.append('Overall')
                logger.line(scene_label, indent=4)
                logger.table(
                    cell_data=[labels] + cell_data.T.tolist(),
                    column_headers=['Event', 'All', 'Training', 'Validation', 'Val amount (%)'],
                    column_types=['str20', 'int', 'int', 'int', 'float1'],
                    column_separators=[0, 1, 3],
                    row_separators=[len(labels)-1],
                    indent=6
                )

        return validation_files

    def validation_files_balanced(self,
                                  fold=None, validation_amount=0.3, seed=0,
                                  verbose=False, scene_label=None, iterations=100,
                                  **kwargs):
        """List of validation files randomly selecting while maintaining data balance.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        validation_amount : float
            Amount of training material to be assigned for validation.

        seed : int
            Randomization seed

        verbose : bool
            Show information about the validation set.

        scene_label : str
            Scene label of the validation set. If None, all training material used.

        iterations : int
            How many randomization iterations will be done before selecting best matched.

        Returns
        -------
        list of str
            List containing all files assigned for validation

        """

        from sklearn.metrics import mean_absolute_error

        random.seed(seed)
        training_meta = self.train(fold=fold, scene_label=scene_label)

        if scene_label:
            scene_labels = [scene_label]
        else:
            scene_labels = self.scene_labels()

        # Check do we have location/source identifier present
        identifier_present = False
        for item in training_meta:
            if item.identifier:
                identifier_present = True
                break

        if identifier_present:
            # Do the balance based on scene class, identifier and event class
            data = {}
            for scene_id, scene_label in enumerate(scene_labels):
                scene_meta = training_meta.filter(scene_label=scene_label)
                data[scene_label] = {}
                for identifier in scene_meta.unique_identifiers:
                    data[scene_label][identifier] = scene_meta.filter(identifier=identifier).unique_files

            # Get event amounts per class
            event_amounts = {}
            for scene_id, scene_label in enumerate(scene_labels):
                event_amounts[scene_label] = {}
                for identifier in list(data[scene_label].keys()):
                    for audio_filename in data[scene_label][identifier]:
                        current_event_amounts = training_meta.filter(filename=audio_filename).event_stat_counts()

                        for event_label, count in iteritems(current_event_amounts):
                            if event_label not in event_amounts[scene_label]:
                                event_amounts[scene_label][event_label] = 0

                            event_amounts[scene_label][event_label] += count

            validation_files = []
            for scene_id, scene_label in enumerate(scene_labels):
                # Optimize scene sets separately
                validation_set_candidates = []
                validation_set_mae = []
                validation_set_event_amounts = []
                training_set_event_amounts = []

                iteration_progress = tqdm(
                    range(0, iterations),
                    desc="{0: <25s}".format('Generate validation split candidates'),
                    file=sys.stdout,
                    leave=False,
                    disable=self.disable_progress_bar,
                    ascii=self.use_ascii_progress_bar
                )

                for i in iteration_progress:
                    identifiers = list(data[scene_label].keys())
                    random.shuffle(identifiers, random.random)

                    valid_percentage_index = int(numpy.ceil(validation_amount * len(identifiers)))

                    current_validation_files = []
                    for loc_id in identifiers[0:valid_percentage_index]:
                        current_validation_files += data[scene_label][loc_id]

                    current_training_files = []
                    for loc_id in identifiers[valid_percentage_index:]:
                        current_training_files += data[scene_label][loc_id]

                    # Event count in training set candidate
                    training_set_event_counts = numpy.zeros(len(event_amounts[scene_label]))
                    for audio_filename in current_training_files:
                        current_event_amounts = training_meta.filter(filename=audio_filename).event_stat_counts()
                        for event_label_id, event_label in enumerate(event_amounts[scene_label]):
                            if event_label in current_event_amounts:
                                training_set_event_counts[event_label_id] += current_event_amounts[event_label]

                    # Accept only sets which leave at least one example for training
                    if numpy.all(training_set_event_counts > 0):
                        # Event counts in validation set candidate
                        validation_set_event_counts = numpy.zeros(len(event_amounts[scene_label]))
                        for audio_filename in current_validation_files:
                            current_event_amounts = training_meta.filter(filename=audio_filename).event_stat_counts()

                            for event_label_id, event_label in enumerate(event_amounts[scene_label]):
                                if event_label in current_event_amounts:
                                    validation_set_event_counts[event_label_id] += current_event_amounts[event_label]

                        # Accept only sets which have examples from each event class
                        if numpy.all(validation_set_event_counts > 0):
                            current_validation_amount = validation_set_event_counts / (validation_set_event_counts + training_set_event_counts)
                            validation_set_candidates.append(current_validation_files)
                            validation_set_mae.append(
                                mean_absolute_error(
                                    numpy.ones(len(current_validation_amount)) * validation_amount,
                                    current_validation_amount)
                            )
                            validation_set_event_amounts.append(validation_set_event_counts)
                            training_set_event_amounts.append(training_set_event_counts)

                # Generate balance validation set
                # Selection done based on event counts (per scene class)
                # Target count specified percentage of training event count
                if validation_set_mae:
                    best_set_id = numpy.argmin(validation_set_mae)
                    validation_files += validation_set_candidates[best_set_id]

                else:
                    message = '{name}: Validation setup creation was not successful! Could not find a set with ' \
                              'examples for each event class in both training and validation.'.format(
                                name=self.__class__.__name__
                              )

                    self.logger.exception(message)
                    raise AssertionError(message)

        else:
            # Do the balance based on scene class, identifier and event class
            data = {}
            for scene_id, scene_label in enumerate(scene_labels):
                data[scene_label] = training_meta.filter(scene_label=scene_label).unique_files

            # Get event amounts per class
            event_amounts = {}
            for scene_id, scene_label in enumerate(scene_labels):
                event_amounts[scene_label] = {}
                for audio_filename in data[scene_label]:
                    current_event_amounts = training_meta.filter(filename=audio_filename).event_stat_counts()

                    for event_label, count in iteritems(current_event_amounts):
                        if event_label not in event_amounts[scene_label]:
                            event_amounts[scene_label][event_label] = 0

                        event_amounts[scene_label][event_label] += count

            validation_files = []
            for scene_id, scene_label in enumerate(scene_labels):
                # Optimize scene sets separately
                validation_set_candidates = []
                validation_set_mae = []
                validation_set_event_amounts = []
                training_set_event_amounts = []

                iteration_progress = tqdm(range(0, iterations),
                                          desc="{0: <25s}".format('Generate validation split candidates'),
                                          file=sys.stdout,
                                          leave=False,
                                          disable=self.disable_progress_bar,
                                          ascii=self.use_ascii_progress_bar)

                for i in iteration_progress:
                    item_ids = list(range(0, len(data[scene_label])))
                    random.shuffle(item_ids, random.random)

                    valid_percentage_index = int(numpy.ceil(validation_amount * len(item_ids)))

                    current_validation_files = []
                    for loc_id in item_ids[0:valid_percentage_index]:
                        current_validation_files.append(data[scene_label][loc_id])

                    current_training_files = []
                    for loc_id in item_ids[valid_percentage_index:]:
                        current_training_files.append(data[scene_label][loc_id])

                    # Event count in training set candidate
                    training_set_event_counts = numpy.zeros(len(event_amounts[scene_label]))
                    for audio_filename in current_training_files:
                        current_event_amounts = training_meta.filter(filename=audio_filename).event_stat_counts()
                        for event_label_id, event_label in enumerate(event_amounts[scene_label]):
                            if event_label in current_event_amounts:
                                training_set_event_counts[event_label_id] += current_event_amounts[event_label]

                    # Accept only sets which leave at least one example for training
                    if numpy.all(training_set_event_counts > 0):
                        # Event counts in validation set candidate
                        validation_set_event_counts = numpy.zeros(len(event_amounts[scene_label]))
                        for audio_filename in current_validation_files:
                            current_event_amounts = training_meta.filter(filename=audio_filename).event_stat_counts()

                            for event_label_id, event_label in enumerate(event_amounts[scene_label]):
                                if event_label in current_event_amounts:
                                    validation_set_event_counts[event_label_id] += current_event_amounts[event_label]

                        # Accept only sets which have examples from each event class
                        if numpy.all(validation_set_event_counts > 0):
                            current_validation_amount = validation_set_event_counts / (validation_set_event_counts + training_set_event_counts)
                            validation_set_candidates.append(current_validation_files)
                            validation_set_mae.append(
                                mean_absolute_error(
                                    numpy.ones(len(current_validation_amount)) * validation_amount,
                                    current_validation_amount)
                            )
                            validation_set_event_amounts.append(validation_set_event_counts)
                            training_set_event_amounts.append(training_set_event_counts)

                # Generate balance validation set
                # Selection done based on event counts (per scene class)
                # Target count specified percentage of training event count
                if validation_set_mae:
                    best_set_id = numpy.argmin(validation_set_mae)
                    validation_files += validation_set_candidates[best_set_id]

                else:
                    message = '{name}: Validation setup creation was not successful! Could not find a set with ' \
                              'examples for each event class in both training and validation.'.format(
                        name=self.__class__.__name__
                    )

                    self.logger.exception(message)
                    raise AssertionError(message)

        if verbose:
            logger = FancyLogger()
            logger.sub_header('Validation set for fold [{fold}] / balanced'.format(fold=fold), indent=2)
            for scene_id, scene_label in enumerate(scene_labels):
                all_stats = training_meta.filter(scene_label=scene_label).event_stat_counts()
                validation_stats = training_meta.filter(scene_label=scene_label, file_list=validation_files).event_stat_counts()
                training_files = sorted(list(set(self.train(fold=fold).unique_files) - set(validation_files)))
                training_stats = training_meta.filter(scene_label=scene_label, file_list=training_files).event_stat_counts()

                cell_data = numpy.zeros((len(list(all_stats.keys())) + 1, 4))
                for event_id, event_label in enumerate(list(all_stats.keys())):
                    cell_data[event_id, 0] = all_stats[event_label]
                    if event_label in training_stats:
                        cell_data[event_id, 1] = training_stats[event_label]

                    if event_label in validation_stats:
                        cell_data[event_id, 2] = validation_stats[event_label]

                    cell_data[event_id, 3] = cell_data[event_id, 2] / float(cell_data[event_id, 0]) * 100

                cell_data[-1, 0] = numpy.sum(list(all_stats.values()))
                cell_data[-1, 1] = numpy.sum(list(training_stats.values()))
                cell_data[-1, 2] = numpy.sum(list(validation_stats.values()))
                cell_data[-1, 3] = cell_data[-1, 2] / float(cell_data[-1, 0]) * 100

                labels = list(all_stats.keys())
                labels.append('Overall')
                logger.line(scene_label, indent=4)
                logger.table(
                    cell_data=[labels] + cell_data.T.tolist(),
                    column_headers=['Event', 'All', 'Training', 'Validation', 'Val amount (%)'],
                    column_types=['str20', 'int', 'int', 'int', 'float1'],
                    column_separators=[0, 1, 3],
                    row_separators=[len(labels)-1],
                    indent=6
                )

        return validation_files


class SyntheticSoundEventDataset(SoundEventDataset):
    def __init__(self, *args, **kwargs):
        super(SyntheticSoundEventDataset, self).__init__(*args, **kwargs)

    def initialize(self):
        """Initialize the dataset, download, extract files and prepare the dataset for the usage.

        Returns
        -------
        self

        """

        # Create the dataset path if does not exist
        Path().makedirs(path=self.local_path)

        if not self.check_filelist():
            self.download_packages()
            self.extract_packages()
            self.load()
            self.prepare()
            self._save_filelist_hash()

        self.synthesize()

        return self

    def synthesize(self):
        pass


class AudioTaggingDataset(Dataset):
    def __init__(self, *args, **kwargs):
        super(AudioTaggingDataset, self).__init__(*args, **kwargs)

    def validation_files_random(self,
                                fold=None, validation_amount=0.3, seed=0, verbose=False,
                                **kwargs):
        """List of validation files selected randomly from the training material.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        validation_amount : float
            Amount of training material to be assigned for validation.

        seed : int
            Randomization seed

        verbose : bool
            Show information about the validation set.

        Returns
        -------
        list of str
            List containing all files assigned for validation

        """

        random.seed(seed)
        training_meta = self.train(fold=fold)

        scene_labels = self.scene_labels()

        training_files = training_meta.unique_files
        random.shuffle(training_files, random.random)

        validation_split_index = int(numpy.ceil(validation_amount * len(training_files)))
        validation_files = training_files[0:validation_split_index]

        if verbose:
            logger = FancyLogger()
            logger.sub_header('Validation set for fold [{fold}] / random'.format(fold=fold), indent=2)
            for scene_id, scene_label in enumerate(scene_labels):
                all_stats = training_meta.filter(scene_label=scene_label).tag_stat_counts()
                validation_stats = training_meta.filter(scene_label=scene_label, file_list=validation_files).tag_stat_counts()
                training_files = sorted(list(set(self.train(fold=fold).unique_files) - set(validation_files)))
                training_stats = training_meta.filter(scene_label=scene_label, file_list=training_files).tag_stat_counts()

                cell_data = numpy.zeros((len(list(all_stats.keys())) + 1, 4))
                for event_id, event_label in enumerate(list(all_stats.keys())):
                    cell_data[event_id, 0] = all_stats[event_label]
                    if event_label in training_stats:
                        cell_data[event_id, 1] = training_stats[event_label]

                    if event_label in validation_stats:
                        cell_data[event_id, 2] = validation_stats[event_label]

                    cell_data[event_id, 3] = cell_data[event_id, 2] / float(cell_data[event_id, 0]) * 100

                cell_data[-1, 0] = numpy.sum(list(all_stats.values()))
                cell_data[-1, 1] = numpy.sum(list(training_stats.values()))
                cell_data[-1, 2] = numpy.sum(list(validation_stats.values()))
                cell_data[-1, 3] = cell_data[-1, 2] / float(cell_data[-1, 0]) * 100

                labels = list(all_stats.keys())
                labels.append('Overall')
                logger.line(scene_label, indent=4)
                logger.table(
                    cell_data=[labels] + cell_data.T.tolist(),
                    column_headers=['Tag', 'All', 'Training', 'Validation', 'Val amount (%)'],
                    column_types=['str20', 'int', 'int', 'int', 'float1'],
                    column_separators=[0, 1, 3],
                    row_separators=[len(labels)-1],
                    indent=6
                )

        return validation_files

    def validation_files_balanced(self,
                                  fold=None, validation_amount=0.3, seed=0, verbose=False, iterations=100,
                                  **kwargs):
        """List of validation files randomly selecting while maintaining data balance.

        Parameters
        ----------
        fold : int
            Fold id, if None all meta data is returned.

        validation_amount : float
            Amount of training material to be assigned for validation.

        seed : int
            Randomization seed

        verbose : bool
            Show information about the validation set.

        iterations : int
            How many randomization iterations will be done before selecting best matched.

        Returns
        -------
        list of str
            List containing all files assigned for validation

        """

        from sklearn.metrics import mean_absolute_error

        random.seed(seed)
        training_meta = self.train(fold=fold)

        # Check do we have location/source identifier present
        identifier_present = False
        for item in training_meta:
            if item.identifier:
                identifier_present = True
                break

        scene_labels = self.scene_labels()

        if identifier_present:
            # Do the balance based on scene class, identifier and event class
            data = {}
            for scene_id, scene_label in enumerate(scene_labels):
                scene_meta = training_meta.filter(scene_label=scene_label)
                data[scene_label] = {}
                for identifier in scene_meta.unique_identifiers:
                    data[scene_label][identifier] = scene_meta.filter(identifier=identifier).unique_files

            # Get tag amounts per class
            tag_amounts = {}
            for scene_id, scene_label in enumerate(scene_labels):
                tag_amounts[scene_label] = {}
                for identifier in list(data[scene_label].keys()):
                    for audio_filename in data[scene_label][identifier]:
                        current_tag_amounts = training_meta.filter(filename=audio_filename).tag_stat_counts()

                        for tag_label, count in iteritems(current_tag_amounts):
                            if tag_label not in tag_amounts[scene_label]:
                                tag_amounts[scene_label][tag_label] = 0

                            tag_amounts[scene_label][tag_label] += count

            validation_files = []
            for scene_id, scene_label in enumerate(scene_labels):
                # Optimize scene sets separately
                validation_set_candidates = []
                validation_set_mae = []
                validation_set_tag_amounts = []
                training_set_tag_amounts = []

                iteration_progress = tqdm(
                    range(0, iterations),
                    desc="{0: <25s}".format('Generate validation split candidates'),
                    file=sys.stdout,
                    leave=False,
                    disable=self.disable_progress_bar,
                    ascii=self.use_ascii_progress_bar
                )

                for i in iteration_progress:

                    identifiers = list(data[scene_label].keys())
                    random.shuffle(identifiers, random.random)

                    valid_percentage_index = int(numpy.ceil(validation_amount * len(identifiers)))

                    current_validation_files = []
                    for loc_id in identifiers[0:valid_percentage_index]:
                        current_validation_files += data[scene_label][loc_id]

                    current_training_files = []
                    for loc_id in identifiers[valid_percentage_index:]:
                        current_training_files += data[scene_label][loc_id]

                    # Tag count in training set candidate
                    training_set_tag_counts = numpy.zeros(len(tag_amounts[scene_label]))
                    for audio_filename in current_training_files:
                        current_tag_amounts = training_meta.filter(filename=audio_filename).tag_stat_counts()
                        for tag_label_id, tag_label in enumerate(tag_amounts[scene_label]):
                            if tag_label in current_tag_amounts:
                                training_set_tag_counts[tag_label_id] += current_tag_amounts[tag_label]

                    # Accept only sets which leave at least one example for training
                    if numpy.all(training_set_tag_counts > 0):
                        # Tag counts in validation set candidate
                        validation_set_tag_counts = numpy.zeros(len(tag_amounts[scene_label]))
                        for audio_filename in current_validation_files:
                            current_tag_amounts = training_meta.filter(filename=audio_filename).tag_stat_counts()

                            for tag_label_id, tag_label in enumerate(tag_amounts[scene_label]):
                                if tag_label in current_tag_amounts:
                                    validation_set_tag_counts[tag_label_id] += current_tag_amounts[tag_label]

                        # Accept only sets which have examples from each tag class
                        if numpy.all(validation_set_tag_counts > 0):
                            current_validation_amount = validation_set_tag_counts / (validation_set_tag_counts + training_set_tag_counts)
                            validation_set_candidates.append(current_validation_files)
                            validation_set_mae.append(
                                mean_absolute_error(
                                    numpy.ones(len(current_validation_amount)) * validation_amount,
                                    current_validation_amount)
                            )
                            validation_set_tag_amounts.append(validation_set_tag_counts)
                            training_set_tag_amounts.append(training_set_tag_counts)

                # Generate balance validation set
                # Selection done based on event counts (per scene class)
                # Target count specified percentage of training event count
                if validation_set_mae:
                    best_set_id = numpy.argmin(validation_set_mae)
                    validation_files += validation_set_candidates[best_set_id]

                else:
                    message = '{name}: Validation setup creation was not successful! Could not find a set with ' \
                              'examples for each tag class in both training and validation.'.format(
                        name=self.__class__.__name__
                    )

                    self.logger.exception(message)
                    raise AssertionError(message)
        else:
            # Do the balance based on scene class, identifier and event class
            data = {}
            for scene_id, scene_label in enumerate(scene_labels):
                data[scene_label] = training_meta.filter(scene_label=scene_label).unique_files

            # Get tag amounts per class
            tag_amounts = {}
            for scene_id, scene_label in enumerate(scene_labels):
                tag_amounts[scene_label] = {}
                for audio_filename in data[scene_label]:
                    current_tag_amounts = training_meta.filter(filename=audio_filename).tag_stat_counts()

                    for tag_label, count in iteritems(current_tag_amounts):
                        if tag_label not in tag_amounts[scene_label]:
                            tag_amounts[scene_label][tag_label] = 0

                        tag_amounts[scene_label][tag_label] += count

            validation_files = []
            for scene_id, scene_label in enumerate(scene_labels):
                # Optimize scene sets separately
                validation_set_candidates = []
                validation_set_mae = []
                validation_set_tag_amounts = []
                training_set_tag_amounts = []

                iteration_progress = tqdm(range(0, iterations),
                                          desc="{0: <25s}".format('Generate validation split candidates'),
                                          file=sys.stdout,
                                          leave=False,
                                          disable=self.disable_progress_bar,
                                          ascii=self.use_ascii_progress_bar)

                for i in iteration_progress:
                    items_id = list(range(0, len(data[scene_label])))
                    random.shuffle(items_id, random.random)

                    valid_percentage_index = int(numpy.ceil(validation_amount * len(items_id)))

                    current_validation_files = []
                    for loc_id in items_id[0:valid_percentage_index]:
                        current_validation_files.append(data[scene_label][loc_id])

                    current_training_files = []
                    for loc_id in items_id[valid_percentage_index:]:
                        current_training_files.append(data[scene_label][loc_id])

                    # Tag count in training set candidate
                    training_set_tag_counts = numpy.zeros(len(tag_amounts[scene_label]))
                    for audio_filename in current_training_files:
                        current_tag_amounts = training_meta.filter(filename=audio_filename).tag_stat_counts()
                        for tag_label_id, tag_label in enumerate(tag_amounts[scene_label]):
                            if tag_label in current_tag_amounts:
                                training_set_tag_counts[tag_label_id] += current_tag_amounts[tag_label]

                    # Accept only sets which leave at least one example for training
                    if numpy.all(training_set_tag_counts > 0):
                        # Tag counts in validation set candidate
                        validation_set_tag_counts = numpy.zeros(len(tag_amounts[scene_label]))
                        for audio_filename in current_validation_files:
                            current_tag_amounts = training_meta.filter(filename=audio_filename).tag_stat_counts()

                            for tag_label_id, tag_label in enumerate(tag_amounts[scene_label]):
                                if tag_label in current_tag_amounts:
                                    validation_set_tag_counts[tag_label_id] += current_tag_amounts[tag_label]

                        # Accept only sets which have examples from each tag class
                        if numpy.all(validation_set_tag_counts > 0):
                            current_validation_amount = validation_set_tag_counts / (
                                validation_set_tag_counts + training_set_tag_counts)
                            validation_set_candidates.append(current_validation_files)
                            validation_set_mae.append(
                                mean_absolute_error(
                                    numpy.ones(len(current_validation_amount)) * validation_amount,
                                    current_validation_amount)
                            )
                            validation_set_tag_amounts.append(validation_set_tag_counts)
                            training_set_tag_amounts.append(training_set_tag_counts)

                # Generate balance validation set
                # Selection done based on event counts (per scene class)
                # Target count specified percentage of training event count
                if validation_set_mae:
                    best_set_id = numpy.argmin(validation_set_mae)
                    validation_files += validation_set_candidates[best_set_id]

                else:
                    message = '{name}: Validation setup creation was not successful! Could not find a set with ' \
                              'examples for each tag class in both training and validation.'.format(
                        name=self.__class__.__name__
                    )

                    self.logger.exception(message)
                    raise AssertionError(message)

        if verbose:
            logger = FancyLogger()
            logger.sub_header('Validation set for fold [{fold}] / balanced'.format(fold=fold), indent=2)
            for scene_id, scene_label in enumerate(scene_labels):
                all_stats = training_meta.filter(scene_label=scene_label).tag_stat_counts()
                validation_stats = training_meta.filter(scene_label=scene_label, file_list=validation_files).tag_stat_counts()
                training_files = sorted(list(set(self.train(fold=fold).unique_files) - set(validation_files)))
                training_stats = training_meta.filter(scene_label=scene_label, file_list=training_files).tag_stat_counts()

                cell_data = numpy.zeros((len(list(all_stats.keys())) + 1, 4))
                for tag_id, tag_label in enumerate(list(all_stats.keys())):
                    cell_data[tag_id, 0] = all_stats[tag_label]
                    if tag_label in training_stats:
                        cell_data[tag_id, 1] = training_stats[tag_label]

                    if tag_label in validation_stats:
                        cell_data[tag_id, 2] = validation_stats[tag_label]

                    cell_data[tag_id, 3] = cell_data[tag_id, 2] / float(cell_data[tag_id, 0]) * 100

                cell_data[-1, 0] = numpy.sum(list(all_stats.values()))
                cell_data[-1, 1] = numpy.sum(list(training_stats.values()))
                cell_data[-1, 2] = numpy.sum(list(validation_stats.values()))
                cell_data[-1, 3] = cell_data[-1, 2] / float(cell_data[-1, 0]) * 100

                labels = list(all_stats.keys())
                labels.append('Overall')
                logger.line(scene_label, indent=4)
                logger.table(
                    cell_data=[labels] + cell_data.T.tolist(),
                    column_headers=['Tag', 'All', 'Training', 'Validation', 'Val amount (%)'],
                    column_types=['str20', 'int', 'int', 'int', 'float1'],
                    column_separators=[0, 1, 3],
                    row_separators=[len(labels)-1],
                    indent=6
                )

        return validation_files
