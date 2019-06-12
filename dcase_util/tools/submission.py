#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import os

from dcase_util.ui import FancyLogger
from dcase_util.containers import DictContainer, MetaDataContainer, \
    ProbabilityContainer, ParameterContainer, ObjectContainer
from dcase_util.utils import FileFormat
from dcase_util.ui import FancyStringifier


class SubmissionChecker(ObjectContainer):
    """Submission meta data and system output checker class"""
    def __init__(self, entry_label, mode='submission',
                 class_labels=None, file_count=None, task='ASC',
                 allow_placeholder_lines_in_output=False,
                 allowed_empty_fields_in_meta=None):
        """Constructor

        Parameters
        ----------
        entry_label : str
            Entry label

        mode : str
            Checker mode [submission, processed]

        class_labels : list of str
            Class labels

        file_count : int
            Correct mount of unique files in the system output

        task : str
            Task label [ASC, SED, TAG]

        allow_placeholder_lines_in_output : bool
            Allow placeholder lines in the output, in case of sound event system output only audio file is outputted
            if no sound events were detected for the file.

        """

        # Run super init
        super(SubmissionChecker, self).__init__()

        self.entry = entry_label
        self.mode = mode
        self.class_labels = class_labels
        self.file_count = file_count
        self.task = task
        self.allow_placeholder_lines_in_output = allow_placeholder_lines_in_output
        self.allowed_empty_fields_in_meta = allowed_empty_fields_in_meta

        self.ui = FancyLogger()
        self.stringifier = FancyStringifier()

    def process(self,
                entry_meta_filename=None,
                entry_results1_filename=None,
                entry_results2_filename=None,
                entry_info_filename=None,
                meta_template=None):
        """Process submission entry and apply all check-ups

        Parameters
        ----------
        entry_meta_filename : str, optional
            File path to the meta file
            Default value None

        entry_results1_filename : str, optional
            File path to system output file
            Default value None

        entry_results2_filename : str, optional
            File path to system output file
            Default value None

        entry_info_filename : str, optional
            File path to extra info file
            Default value None

        meta_template : dict, optional
            Meta template dictionary to compare against.
            Default value None

        Returns
        -------
        self

        """
        error_log = []
        meta = None
        results1 = None
        results2 = None

        # Check files
        if entry_meta_filename:
            meta, err = self._parameter_file(filename=entry_meta_filename)
            error_log += err

        if entry_results1_filename:
            results1, err = self._system_output_file(
                filename=entry_results1_filename
            )
            error_log += err

        if entry_results2_filename:
            results2, err = self._system_output_file(
                filename=entry_results2_filename
            )
            error_log += err

        if entry_info_filename:
            info, err = self._parameter_file(
                filename=entry_info_filename
            )
            error_log += err

        if meta and not meta_template:
            # Do meta data checking without comparing to template
            error_log += self._main_structure(meta)
            error_log += self._submission_info(submission=meta['submission'])
            error_log += self._system_meta(
                results=meta['results'],
                check_evaluation_dataset=True if self.mode == 'processed' else False
            )
            error_log += self._system_description(meta=meta['system']['description'])
            error_log += self._system_complexity(meta=meta['system']['complexity'])

        elif meta and meta_template:
            error_log += self._compare_meta(template=meta_template, meta=meta, allowed_empty_fields=self.allowed_empty_fields_in_meta)

        if results1:
            error_log += self._system_output(output=results1)

        if results2:
            error_log += self._system_output(output=results2)

        return error_log

    def _parameter_file(self, filename):
        """Checks that ParameterContainer (yaml) exists, and can be parsed.

        Parameters
        ----------
        filename : str
            File path

        Raises
        ------
        ImportError:
            Error if file format specific module cannot be imported
        IOError:
            File does not exists or has unknown file format

        Returns
        -------
        ParameterContainer or bool
        error_log, list of str

        """
        error_log = []

        if not os.path.isfile(filename):
            error_log.append(
                self._file_error_message(
                    type_label='Exists',
                    subtype_label='Parameter file',
                    description='{filename:s}'.format(
                        filename=filename
                    )
                )
            )

            return False, error_log

        else:
            return ParameterContainer().load(
                filename=filename
            ), error_log

    def _system_output_file(self, filename):
        """Checks that MetaDataContainer file exists, and can be parsed.

        Parameters
        ----------
        filename : str
            File path

        Raises
        ------
        ImportError:
            Error if file format specific module cannot be imported
        IOError:
            File does not exists or has unknown file format

        Returns
        -------
        MetaDataContainer or bool
        error_log, list of str

        """

        error_log = []

        if not os.path.isfile(filename):
            error_log.append(
                self._file_error_message(
                    type_label='Exists',
                    subtype_label='Output file',
                    description='{filename:s}'.format(
                        filename=filename
                    )
                )
            )

            return False, error_log

        else:
            try:
                if self.task == 'TAG':
                    data = ProbabilityContainer().load(
                        filename=filename
                    )

                elif self.task == 'ASC':
                    if FileFormat.detect(filename) == FileFormat.CSV:
                        data = MetaDataContainer().load(
                            filename=filename,
                            csv_header=False,
                            fields=['filename', 'scene_label']
                        )

                    else:
                        data = MetaDataContainer().load(
                            filename=filename
                        )

                else:

                    data = MetaDataContainer().load(
                        filename=filename
                    )

                return data, error_log

            except Exception:
                error_log.append(
                    self._file_error_message(
                        type_label='Parsing',
                        subtype_label='Output file',
                        description='{filename:s}'.format(
                            filename=filename
                        )
                    )
                )

                return False, error_log

    def _main_structure(self, meta):
        """Check high level structure of meta data

        Parameters
        ----------
        meta : dict
            Meta data

        Returns
        -------
        error_log, list of str

        """
        error_log = []

        if meta.get('system') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.system'
                )
            )

        if meta.get('submission') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.submission'
                )
            )

        if meta.get('results') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.results'
                )
            )

        return error_log

    def _submission_info(self, submission, check_label=True, check_authors=True):
        """Check submission meta data

        Parameters
        ----------
        submission : dict
            Submission meta data

        check_label : bool
            Check submission label

        check_authors : bool
            Check authors

        Returns
        -------
        error_log, list of str

        """

        error_log = []

        if submission.get('abbreviation') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.submission.abbreviation'
                )
            )

        if check_label and submission.get('label') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.submission.label'
                )
            )

        if submission.get('name') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.submission.name'
                )
            )

        if submission.get('authors') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.submission.authors'
                )
            )

        else:
            if check_authors:
                error_log += self._submission_authors(submission.get('authors'))

        return error_log

    def _submission_authors(self, authors):
        """Check submission authors
        Parameters
        ----------
        authors : list of dict
            List of authors dicts.

        Returns
        -------
        error_log, list of str

        """

        error_log = []

        if not isinstance(authors, list):
            error_log.append(u'Authors not given in list format for the submission')

        for author in authors:
            author = DictContainer(author)
            error_log += self._check_author_information(author=author)

        return error_log

    def _system_meta(self, results, task=None, check_development_dataset=True, check_evaluation_dataset=True):
        """Check system result scores given in the meta data

        Parameters
        ----------
        results : dict
            Result meta data

        task : str, optional
            Temporal override for the task parameter given to class constructor.

        check_development_dataset : bool
            Check development dataset results

        check_evaluation_dataset : bool
            Check evaluation dataset results

        Returns
        -------
        error_log, list of str

        """

        error_log = []

        if task is None:
            task = self.task

        if results is None:
            error_log.append(u'No results section')

        else:
            results = DictContainer(results)
            if check_development_dataset:
                # Check development dataset results

                if results.get('development_dataset') is None:
                    error_log.append(
                        self._meta_error_message(
                            type_label='Field',
                            subtype_label='Missing',
                            description='meta.results.development_dataset'
                        )
                    )

                else:
                    if task == 'ASC':
                        if results.get_path('development_dataset.overall.accuracy') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.overall.accuracy'
                                )
                            )

                    elif task == 'SED_event':
                        if results.get_path('development_dataset.event_based.overall.er') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.event_based.overall.er'
                                )
                            )

                        if results.get_path('development_dataset.event_based.overall.f1') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.event_based.overall.f1'
                                )
                            )

                    elif task == 'SED_segment':
                        if results.get_path('development_dataset.segment_based.overall.er') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.segment_based.overall.er'
                                )
                            )

                        if results.get_path('development_dataset.segment_based.overall.f1') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.segment_based.overall.f1'
                                )
                            )

                    elif task == 'task4':
                        pass

                    # Check development dataset / class wise results
                    if task == 'ASC':
                        if results.get_path('development_dataset.class_wise') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.class_wise'
                                )
                            )

                        else:
                            if len(results.get_path('development_dataset.class_wise')) != len(self.class_labels):
                                error_log.append(
                                    self._meta_error_message(
                                        type_label='Field',
                                        subtype_label='Wrong class count',
                                        description='development_dataset.class_wise [{class_wise:d} != {target:d}]'.format(
                                            class_wise=len(results.get_path('development_dataset.class_wise')),
                                            target=len(self.class_labels)
                                        )
                                    )
                                )

                            for class_label, class_data in iteritems(results.get_path('development_dataset.class_wise')):
                                if 'accuracy' not in class_data or class_data['accuracy'] is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.development_dataset.class_wise.{class_label}'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                    elif task == 'SED_event':
                        if results.get_path('development_dataset.event_based.class_wise') is not None:
                            if len(results.get_path('development_dataset.event_based.class_wise')) != len(self.class_labels):
                                error_log.append(
                                    self._meta_error_message(
                                        type_label='Field',
                                        subtype_label='Wrong class count',
                                        description='development_dataset.event_based.class_wise [{class_wise:d} != {target:d}]'.format(
                                            class_wise=len(results.get_path('development_dataset.event_based.class_wise')),
                                            target=len(self.class_labels)
                                        )
                                    )
                                )

                            for class_label, class_data in iteritems(results.get_path('development_dataset.event_based.class_wise')):
                                if class_data.get('er') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.development_dataset.event_based.class_wise.{class_label}.er'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                                if class_data.get('f1') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.development_dataset.event_based.class_wise.{class_label}.f1'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                        else:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.event_based.class_wise'
                                )
                            )

                    elif task == 'SED_segment':
                        if results.get_path('development_dataset.segment_based.class_wise') is not None:
                            if len(results.get_path('development_dataset.segment_based.class_wise')) != len(self.class_labels):
                                error_log.append(
                                    self._meta_error_message(
                                        type_label='Field',
                                        subtype_label='Wrong class count',
                                        description='development_dataset.segment_based.class_wise [{class_wise:d} != {target:d}]'.format(
                                            class_wise=len(results.get_path('development_dataset.segment_based.class_wise')),
                                            target=len(self.class_labels)
                                        )
                                    )
                                )

                            for class_label, class_data in iteritems(results.get_path('development_dataset.segment_based.class_wise')):
                                if class_data.get('er') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.development_dataset.segment_based.class_wise.{class_label}.er'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                                if class_data.get('f1') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.development_dataset.segment_based.class_wise.{class_label}.f1'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                        else:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.development_dataset.segment_based.class_wise'
                                )
                            )

                    elif task == 'task4':
                        pass

            if check_evaluation_dataset:
                # Check evaluation dataset results
                if 'evaluation_dataset' not in results:
                    error_log.append(
                        self._meta_error_message(
                            type_label='Field',
                            subtype_label='Missing',
                            description='meta.results.evaluation_dataset'
                        )
                    )

                else:
                    if task == 'ASC':
                        if results.get_path('evaluation_dataset.overall') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.overall'
                                )
                            )

                        if results.get_path('evaluation_dataset.class_wise') is not None:
                            if len(results.get_path('evaluation_dataset.class_wise')) != len(self.class_labels):
                                error_log.append(
                                    self._meta_error_message(
                                        type_label='Field',
                                        subtype_label='Wrong class count',
                                        description='evaluation_dataset.class_wise [{class_wise:d} != {target:d}]'.format(
                                            class_wise=len(results.get_path('evaluation_dataset.class_wise')),
                                            target=len(self.class_labels)
                                        )
                                    )
                                )

                            for class_label, class_data in iteritems(results.get_path('evaluation_dataset.class_wise')):
                                if class_data.get('accuracy') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.evaluation_dataset.class_wise.{class_label}.er'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                        else:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.class_wise'
                                )
                            )

                    elif task == 'SED_event':
                        if results.get_path('evaluation_dataset.event_based.overall.er') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.event_based.overall.er'
                                )
                            )

                        if results.get_path('evaluation_dataset.event_based.overall.f1') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.event_based.overall.f1'
                                )
                            )

                        if results.get_path('evaluation_dataset.event_based.class_wise') is not None:
                            if len(results.get_path('evaluation_dataset.event_based.class_wise')) != len(self.class_labels):
                                error_log.append(
                                    self._meta_error_message(
                                        type_label='Field',
                                        subtype_label='Wrong class count',
                                        description='evaluation_dataset.event_based.class_wise [{class_wise:d} != {target:d}]'.format(
                                            class_wise=len(results.get_path('evaluation_dataset.event_based.class_wise')),
                                            target=len(self.class_labels)
                                        )
                                    )
                                )

                            for class_label, class_data in iteritems(results.get_path('evaluation_dataset.event_based.class_wise')):
                                if class_data.get('er') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.evaluation_dataset.event_based.class_wise.{class_label}.er'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                                if class_data.get('f1') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.evaluation_dataset.event_based.class_wise.{class_label}.f1'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                        else:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.event_based.class_wise'
                                )
                            )

                    elif task == 'SED_segment':
                        if results.get_path('evaluation_dataset.segment_based.overall.er') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.segment_based.overall.er'
                                )
                            )

                        if results.get_path('evaluation_dataset.segment_based.overall.f1') is None:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.segment_based.overall.f1'
                                )
                            )

                        if results.get_path('evaluation_dataset.segment_based.class_wise') is not None:
                            if len(results.get_path('evaluation_dataset.segment_based.class_wise')) != len(self.class_labels):
                                error_log.append(
                                    self._meta_error_message(
                                        type_label='Field',
                                        subtype_label='Wrong class count',
                                        description='evaluation_dataset.segment_based.class_wise [{class_wise:d} != {target:d}]'.format(
                                            class_wise=len(results.get_path('evaluation_dataset.segment_based.class_wise')),
                                            target=len(self.class_labels)
                                        )
                                    )
                                )

                            for class_label, class_data in iteritems(results.get_path('evaluation_dataset.segment_based.class_wise')):
                                if class_data.get('er') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.evaluation_dataset.segment_based.class_wise.{class_label}.er'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                                if class_data.get('f1') is None:
                                    error_log.append(
                                        self._meta_error_message(
                                            type_label='Field',
                                            subtype_label='Missing',
                                            description='meta.results.evaluation_dataset.segment_based.class_wise.{class_label}.f1'.format(
                                                class_label=class_label
                                            )
                                        )
                                    )

                        else:
                            error_log.append(
                                self._meta_error_message(
                                    type_label='Field',
                                    subtype_label='Missing',
                                    description='meta.results.evaluation_dataset.segment_based.class_wise'
                                )
                            )

                    elif task == 'task4':
                        pass

        return error_log

    def _system_description(self, meta, style='DCASE2017'):
        """Check system description meta data

        Parameters
        ----------
        meta : dict
            System meta data

        style : str
            Style [DCASE2017, DCASE2016]

        Returns
        -------
        error_log, list of str

        """
        error_log = []

        if style == 'DCASE2016':
            if 'features' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.features'
                    )
                )

            if 'classifier' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.classifier'
                    )
                )

            if 'input' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.input'
                    )
                )

            if 'preprocessing' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.preprocessing'
                    )
                )

            if 'sampling_rate' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.sampling_rate'
                    )
                )

            if 'training_data' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.training_data'
                    )
                )

        else:
            # style == 'DCASE2017':

            if 'acoustic_features' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.acoustic_features'
                    )
                )

            if 'data_augmentation' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.data_augmentation'
                    )
                )

            if 'decision_making' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.decision_making'
                    )
                )

            if 'input_channels' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.input_channels'
                    )
                )

            if 'input_sampling_rate' not in meta:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.input_sampling_rate'
                    )
                )

            if 'acoustic_features' not in meta or meta['acoustic_features'] is None:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.features'
                    )
                )

            if 'machine_learning_method' not in meta or meta['machine_learning_method'] is None:
                error_log.append(
                    self._meta_error_message(
                        type_label='Field',
                        subtype_label='Missing',
                        description='meta.system.description.machine_learning_method'
                    )
                )

        return error_log

    def _system_complexity(self, meta):
        """Check system complexity meta data

        Parameters
        ----------
        meta : dict
            System meta data

        Returns
        -------
        error_log, list of str

        """

        error_log = []

        if 'total_parameters' not in meta:
            error_log.append(
                self._meta_error_message(
                    type_label='Field',
                    subtype_label='Missing',
                    description='meta.system.complexity.total_parameters'
                )
            )

        return error_log

    def _system_output(self, output, task=None, allow_placeholder_lines_in_output=None):
        """Check system result scores given in the meta data

        Parameters
        ----------
        output : MetaDataContainer
            System output

        task : str, optional
            Temporal override for the task parameter given to class constructor.

        allow_placeholder_lines_in_output : bool, optional
            Temporal override for the parameter given to class constructor.

        Returns
        -------
        error_log, list of str

        """

        error_log = []

        if task is None:
            task = self.task

        if allow_placeholder_lines_in_output is None:
            allow_placeholder_lines_in_output = self.allow_placeholder_lines_in_output

        if len(output.unique_files) != self.file_count:
            error_log.append(
                self._output_error_message(
                    type_label='Content',
                    subtype_label='Wrong filename count',
                    description='{current:d} != {target:d}'.format(
                        current=len(output.unique_files),
                        target=self.file_count
                    )
                )
            )

        valid_field_count = True
        invalid_item = None
        invalid_labels = []

        for item in output:
            if task == 'ASC':
                if not item.filename or not item.scene_label:
                    valid_field_count = False

                if item.scene_label not in self.class_labels:
                    if item.scene_label not in invalid_labels:
                        invalid_labels.append(item.scene_label)

            elif task.startswith('SED'):
                fields = sorted(list(item.keys()))
                if allow_placeholder_lines_in_output:
                    if len(fields) == 1 and fields != ['filename']:
                        valid_field_count = False
                        invalid_item = item

                    elif len(fields) > 1:
                        if not item.filename or not item.event_label or item.onset is None or item.offset is None:
                            valid_field_count = False
                            invalid_item = item

                else:
                    if not item.filename or not item.event_label or item.onset is None or item.offset is None:
                        valid_field_count = False
                        invalid_item = item

                if item.event_label not in self.class_labels:
                    if item.event_label not in invalid_labels and item.event_label is not None:
                        invalid_labels.append(item.event_label)

        if not valid_field_count:
            if invalid_item:
                field_count = '{field_count:d}'.format(len(invalid_item))
            else:
                field_count = 'None'

            error_log.append(
                self._output_error_message(
                    type_label='Content',
                    subtype_label='Wrong field count',
                    description='{field_count:s}'.format(
                        field_count=field_count
                    )
                )
            )

        if invalid_labels:
            error_log.append(
                self._output_error_message(
                    type_label='Content',
                    subtype_label='Invalid label',
                    description='{invalid_labels:s}'.format(
                        invalid_labels=', '.join(invalid_labels),
                    )
                )
            )

        return error_log

    def _compare_meta(self, template, meta, allowed_empty_fields=None):
        """Compare meta dictionary against template dictionary

        Parameters
        ----------
        template : dict
            Template dictionary

        meta : dict
            Submission meta data dictionary
            Default value ""

        allowed_empty_fields : list of str
            List of DictContainer paths to fields which are allowed to be empty.
            Default value None

        Returns
        -------
        error_log, list of str

        """

        error_log = []
        if not allowed_empty_fields:
            allowed_empty_fields = []

        # Make sure meta data is in DictContainer
        template = DictContainer(template)
        meta = DictContainer(meta)

        # 1. check main structure
        for main_section in template.keys():
            if main_section not in meta:
                error_log.append(
                    self._error_message(
                        type_label='Section',
                        subtype_label='Missing',
                        description='{main_section}'.format(
                            main_section=main_section
                        ),
                    )
                )

        # Define checking as function to allow recursive call
        def _compare_dictionaries(
                target_dict, dict2, dict2_name, path='',
                match_values=False, check_none=False,
                allowed_empty_fields=None
        ):
            if not allowed_empty_fields:
                allowed_empty_fields = []

            error_log = []
            key_errors = []
            value_errors = []
            old_path = path

            for key in list(target_dict.keys()):
                path = old_path + '.' + str(key)
                if key not in dict2:
                    key_errors.append(
                        self._meta_error_message(
                            type_label='Field',
                            subtype_label='Missing',
                            description='{dict_name}{path}'.format(
                                dict_name=dict2_name,
                                path=path
                            )
                        )
                    )

                else:
                    if isinstance(target_dict[key], dict) and isinstance(dict2[key], dict):
                        # Check nested dictionaries
                        error_log += _compare_dictionaries(
                            target_dict=target_dict[key],
                            dict2=dict2[key],
                            dict2_name=dict2_name,
                            path=path,
                            match_values=match_values,
                            check_none=check_none,
                            allowed_empty_fields=allowed_empty_fields
                        )

                    elif isinstance(target_dict[key], list) and isinstance(dict2[key], list):
                        # Special case handling in case of lists
                        if key == 'authors':
                            for author in dict2[key]:
                                error_log += self._check_author_information(author=author)

                    else:
                        # Check for empty fields
                        if check_none and dict2[key] is None:
                            if path[1:] not in allowed_empty_fields:
                                value_errors.append(
                                    self._meta_error_message(
                                        type_label='Value',
                                        subtype_label='None',
                                        description='{dict_name}{path}'.format(
                                            dict_name=dict2_name,
                                            path=path
                                        )
                                    )
                                )

                        # Match values
                        if match_values and target_dict[key] != dict2[key]:
                            value_errors.append(
                                self._meta_error_message(
                                    type_label='Value',
                                    subtype_label='Mismatch',
                                    description='{path} ({value1}) != ({value2})'.format(
                                        path=path,
                                        value1=target_dict[key],
                                        value2=dict2[key]
                                    )
                                )
                            )

            return key_errors + value_errors + error_log

        error_log += _compare_dictionaries(
            target_dict=template,
            dict2=meta,
            dict2_name='meta',
            match_values=False,
            check_none=True,
            allowed_empty_fields=allowed_empty_fields
        )

        return error_log

    def _check_author_information(self, author):
        """Check submission author information
        Parameters
        ----------
        author : dict
            Author dict

        Returns
        -------
        error_log, list of str

        """

        author = DictContainer(author)
        error_log = []

        if author.get('lastname') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Author',
                    subtype_label='No lastname',
                    description='{last_name:s}, {first_name:s}'.format(
                        last_name=author['lastname'],
                        first_name=author['firstname']
                    )
                )
            )

        if author.get('firstname') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Author',
                    subtype_label='No firstname',
                    description='{last_name:s}, {first_name:s}'.format(
                        last_name=author['lastname'],
                        first_name=author['firstname']
                    )
                )
            )

        if author.get('email') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Author',
                    subtype_label='No email',
                    description='{last_name:s}, {first_name:s}'.format(
                        last_name=author['lastname'],
                        first_name=author['firstname']
                    )
                )
            )

        if author.get('affiliation') is None:
            error_log.append(
                self._meta_error_message(
                    type_label='Author',
                    subtype_label='No affiliation',
                    description='{last_name:s}, {first_name:s}'.format(
                        last_name=author['lastname'],
                        first_name=author['firstname']
                    )
                )
            )

        else:
            if isinstance(author.get('affiliation'), list):
                for a in author.get('affiliation'):
                    if a.get('abbreviation') is None:
                        error_log.append(
                            self._meta_error_message(
                                type_label='Author',
                                subtype_label='No abbreviation',
                                description='{last_name:s}, {first_name:s}'.format(
                                    last_name=author['lastname'],
                                    first_name=author['firstname']
                                )
                            )
                        )

                    if a.get('department') is None:
                        error_log.append(
                            self._error_message(
                                type_label='Author',
                                subtype_label='No department',
                                description='{last_name:s}, {first_name:s}'.format(
                                    last_name=author['lastname'],
                                    first_name=author['firstname']
                                )
                            )
                        )

                    if a.get('institute') is None:
                        error_log.append(
                            self._meta_error_message(
                                type_label='AUTHOR',
                                subtype_label='No institute',
                                description='{last_name:s}, {first_name:s}'.format(
                                    last_name=author['lastname'],
                                    first_name=author['firstname']
                                )
                            )
                        )

                    if a.get('location') is None:
                        error_log.append(
                            self._meta_error_message(
                                type_label='Author',
                                subtype_label='No location',
                                description='{last_name:s}, {first_name:s}'.format(
                                    last_name=author['lastname'],
                                    first_name=author['firstname']
                                )
                            )
                        )

            else:
                if author.get_path('affiliation.abbreviation') is None:
                    error_log.append(
                        self._meta_error_message(
                            type_label='Author',
                            subtype_label='No abbreviation',
                            description='{last_name:s}, {first_name:s}'.format(
                                last_name=author['lastname'],
                                first_name=author['firstname']
                            ),
                        )
                    )

                if author.get_path('affiliation.department') is None:
                    error_log.append(
                        self._meta_error_message(
                            type_label='Author',
                            subtype_label='No department',
                            description='{last_name:s}, {first_name:s}'.format(
                                last_name=author['lastname'],
                                first_name=author['firstname']
                            )
                        )
                    )

                if author.get_path('affiliation.institute') is None:
                    error_log.append(
                        self._meta_error_message(
                            type_label='Author',
                            subtype_label='No institute',
                            description='{last_name:s}, {first_name:s}'.format(
                                last_name=author['lastname'],
                                first_name=author['firstname']
                            ),
                        )
                    )

                if author.get_path('affiliation.location') is None:
                    error_log.append(
                        self._meta_error_message(
                            type_label='Author',
                            subtype_label='No location',
                            description='{last_name:s}, {first_name:s}'.format(
                                last_name=author['lastname'],
                                first_name=author['firstname']
                            ),
                        )
                    )

        return error_log

    def _error_message(self, error_class='', type_label='', subtype_label='', description=''):
        """Error message
        
        Parameters
        ----------
        error_class : str, optional
            Error class
            Default value ""

        type_label : str, optional
            Error type
            Default value ""

        subtype_label : str, optional
            Error sub type
            Default value ""

        message : str, optional
            Error description
            Default value ""

        Returns
        -------
        str

        """

        return u'{error_class} {type_label}  {subtype_label}  {message}'.format(
            error_class=self.stringifier.formatted_value(error_class, data_type='stf6').upper(),
            type_label=self.stringifier.formatted_value(type_label, data_type='stf10').upper(),
            subtype_label=self.stringifier.formatted_value(subtype_label, data_type='stf20'),
            message=description
        )

    def _meta_error_message(self, type_label='', subtype_label='', description=''):
        return self._error_message(
            error_class='Meta',
            type_label=type_label,
            subtype_label=subtype_label,
            description=description
        )

    def _output_error_message(self, type_label='', subtype_label='', description=''):
        return self._error_message(
            error_class='Output',
            type_label=type_label,
            subtype_label=subtype_label,
            description=description
        )

    def _file_error_message(self, type_label='', subtype_label='', description=''):
        return self._error_message(
            error_class='File',
            type_label=type_label,
            subtype_label=subtype_label,
            description=description
        )
