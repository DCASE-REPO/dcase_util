#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import logging
import os

from dcase_util.ui import FancyLogger
from dcase_util.containers import DictContainer, MetaDataContainer, \
    ProbabilityContainer, ParameterContainer, ObjectContainer


class SubmissionChecker(ObjectContainer):
    """Submission meta data and system output checker class"""
    def __init__(self, entry_label, mode='submission', class_labels=None, file_count=None, task='ASC',
                 allow_placeholder_lines_in_output=False):
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
        self.error_log = []
        self.ui = FancyLogger()

    def process(self, entry_meta_filename=None, entry_results1_filename=None, entry_results2_filename=None,
                entry_info_filename=None):
        """Process submission entry and apply all check-ups

        Parameters
        ----------
        entry_meta_filename : str, optional
            File path to the meta file

        entry_results1_filename : str, optional
            File path to system output file

        entry_results2_filename : str, optional
            File path to system output file

        entry_info_filename : str, optional
            File path to extra info file

        Returns
        -------
        self

        """

        meta = None
        results1 = None
        results2 = None

        # Check files
        if entry_meta_filename:
            meta = self.parameter_file(filename=entry_meta_filename)

        if entry_results1_filename:
            results1 = self.system_output_file(filename=entry_results1_filename)

        if entry_results2_filename:
            results2 = self.system_output_file(filename=entry_results2_filename)

        if entry_info_filename:
            info = self.parameter_file(filename=entry_info_filename)

        if meta:
            self.main_structure(meta)
            self.submission_info(submission=meta['submission'])
            self.system_meta(
                results=meta['results'],
                check_evaluation_dataset=True if self.mode == 'processed' else False
            )
            self.system_description(meta=meta['system']['description'])

        if results1:
            self.system_output(output=results1)

        if results2:
            self.system_output(output=results2)

        return self.error_log

    def parameter_file(self, filename):
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

        """

        if not os.path.isfile(filename):
            self.error_log.append(u'File missing [{filename:s}]'.format(
                filename=filename
            ))

            return False

        else:
            return ParameterContainer().load(filename=filename)

    def system_output_file(self, filename):
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

        """

        if not os.path.isfile(filename):
            self.error_log.append(u'File missing [{filename:s}]'.format(
                filename=filename
            ))

            return False

        else:
            try:
                if self.task == 'TAG':
                    data = ProbabilityContainer().load(filename=filename)

                else:
                    data = MetaDataContainer().load(filename=filename)

                return data

            except Exception:
                self.error_log.append(u'File cannot be parsed [{filename:s}]'.format(
                    filename=filename
                ))

    def main_structure(self, meta):
        """Check high level structure of meta data

        Parameters
        ----------
        meta : dict
            Meta data

        Returns
        -------
        self

        """

        if meta.get('system') is None:
            self.error_log.append(u'No system information given for the submission')

        if meta.get('submission') is None:
            self.error_log.append(u'No submission information given for the submission')

        if meta.get('results') is None:
            self.error_log.append(u'No results information given for the submission')

        return self

    def submission_info(self, submission, check_label=True, check_authors=True):
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
        self

        """

        if submission.get('abbreviation') is None:
            self.error_log.append(u'No abbreviation given for the submission')

        if check_label and submission.get('label') is None:
            self.error_log.append(u'No label given for the submission')

        if submission.get('name') is None:
            self.error_log.append(u'No name given for the submission')

        if submission.get('authors') is None:
            self.error_log.append(u'No authors given for the submission')

        else:
            if check_authors:
                self.submission_authors(submission.get('authors'))

        return self

    def submission_authors(self, authors, check_email=True, check_affiliation=True,
                           check_affiliation_abbreviation=True, check_affiliation_department=True):
        """Check submission authors
        Parameters
        ----------
        authors : list of dict
            List of authors dicts.

        check_email : bool
            Check that author email exists.

        check_affiliation : bool
            Check author affiliation.

        check_affiliation_abbreviation : bool
            Check that affiliation abbreviation exists.

        check_affiliation_department : bool
            Check that affiliation has department defined.

        Returns
        -------
        self

        """

        if not isinstance(authors, list):
            self.error_log.append(u'Authors not given in list format for the submission')

        for author in authors:
            author = DictContainer(author)

            if author.get('lastname') is None:
                self.error_log.append(u'No lastname given for author ({last_name:s}, {first_name:s})'.format(
                    last_name=author['lastname'],
                    first_name=author['firstname']))

            if author.get('firstname') is None:
                self.error_log.append(u'No firstname given for author ({last_name:s}, {first_name:s})'.format(
                    last_name=author['lastname'],
                    first_name=author['firstname']))

            if check_email:
                if author.get('email') is None:
                    self.error_log.append(u'No email given for author ({last_name:s}, {first_name:s})'.format(
                        last_name=author['lastname'],
                        first_name=author['firstname']))

            if check_affiliation:
                if author.get('affiliation') is None:
                    self.error_log.append(u'No affiliation given for author ({last_name:s}, {first_name:s})'.format(
                        last_name=author['lastname'],
                        first_name=author['firstname']))

                else:
                    if isinstance(author.get('affiliation'), list):
                        for a in author.get('affiliation'):
                            affiliation = ', '.join(filter(None, list(a.values())))
                            if check_affiliation_abbreviation:
                                if a.get('abbreviation') is None:
                                    self.error_log.append(
                                        u'No abbreviation given ({last_name:s}, {first_name:s}, {affiliation:s})'.format(
                                            last_name=author['lastname'],
                                            first_name=author['firstname'],
                                            affiliation=affiliation
                                        ))

                            if check_affiliation_department:
                                if a.get('department') is None:
                                    self.error_log.append(
                                        u'No department given ({last_name:s}, {first_name:s}, {affiliation:s})'.format(
                                            last_name=author['lastname'],
                                            first_name=author['firstname'],
                                            affiliation=affiliation
                                        ))

                            if a.get('institute') is None:
                                self.error_log.append(
                                    u'No institute given ({last_name:s}, {first_name:s}, {affiliation:s})'.format(
                                        last_name=author['lastname'],
                                        first_name=author['firstname'],
                                        affiliation=affiliation
                                    ))

                            if a.get('location') is None:
                                self.error_log.append(
                                    u'No location given ({last_name:s}, {first_name:s}, {affiliation:s})'.format(
                                        last_name=author['lastname'],
                                        first_name=author['firstname'],
                                        affiliation=affiliation
                                    ))

                    else:
                        affiliation = ', '.join(filter(None, list(author['affiliation'].values())))
                        if check_affiliation_abbreviation:
                            if author.get_path('affiliation.abbreviation') is None:
                                self.error_log.append(
                                    u'No abbreviation given ({last_name:s}, {first_name:s}, {affiliation:s})'.format(
                                        last_name=author['lastname'],
                                        first_name=author['firstname'],
                                        affiliation=affiliation
                                    ))
                        if check_affiliation_department:
                            if author.get_path('affiliation.department') is None:
                                self.error_log.append(
                                    u'No department given ({last_name:s}, {first_name:s}, {affiliation:s})'.format(
                                        last_name=author['lastname'],
                                        first_name=author['firstname'],
                                        affiliation=affiliation
                                    ))
                        if author.get_path('affiliation.institute') is None:
                            self.error_log.append(
                                u'No institute given ({last_name:s}, {first_name:s}, {affiliation:s})'.format(
                                    last_name=author['lastname'],
                                    first_name=author['firstname'],
                                    affiliation=affiliation
                                ))

                        if author.get_path('affiliation.location') is None:
                            self.error_log.append(
                                u'No location given ({last_name:s}, {first_name:s})'.format(
                                    last_name=author['lastname'],
                                    first_name=author['firstname'],
                                    affiliation=affiliation
                                ))
        return self

    def system_meta(self, results, task=None, check_development_dataset=True, check_evaluation_dataset=True):
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
        self

        """

        if task is None:
            task = self.task

        if results is None:
            self.error_log.append(u'No results section')

        else:
            results = DictContainer(results)
            if check_development_dataset:
                # Check development dataset results

                if results.get('development_dataset') is None:
                    self.error_log.append(u'No development results given')

                else:
                    if task == 'ASC':
                        if results.get_path('development_dataset.overall.accuracy') is None:
                            self.error_log.append(u'No development overall result given ')

                    elif task == 'SED_event':
                        if results.get_path('development_dataset.event_based.overall.er') is None:
                            self.error_log.append(u'No development overall result given [event_based.overall.er]')

                        if results.get_path('development_dataset.event_based.overall.f1') is None:
                            self.error_log.append(u'No development overall result given [event_based.overall.f1]')

                    elif task == 'SED_segment':
                        if results.get_path('development_dataset.segment_based.overall.er') is None:
                            self.error_log.append(u'No development overall result given [segment_based.overall.er]')

                        if results.get_path('development_dataset.segment_based.overall.f1') is None:
                            self.error_log.append(u'No development overall result given [segment_based.overall.f1]')

                    elif task == 'task4':
                        pass

                    # Check development dataset / class wise results
                    if task == 'ASC':
                        if results.get_path('development_dataset.class_wise') is None:
                            self.error_log.append(u'No class_wise development results given')

                        else:
                            if len(results.get_path('development_dataset.class_wise')) != len(self.class_labels):
                                self.error_log.append(u'Incorrect number class-wise development results given [{class_wise:d}/{target:d}]'.format(
                                    class_wise=len(results.get_path('development_dataset.class_wise')),
                                    target=len(self.class_labels)
                                ))

                            for class_label, class_data in iteritems(results.get_path('development_dataset.class_wise')):
                                if 'accuracy' not in class_data or class_data['accuracy'] is None:
                                    self.error_log.append(u'Incorrect class-wise development results given for [{class_label:s}]'.format(
                                            class_label=class_label
                                    ))

                    elif task == 'SED_event':
                        if results.get_path('development_dataset.event_based.class_wise') is not None:
                            if len(results.get_path('development_dataset.event_based.class_wise')) != len(self.class_labels):
                                self.error_log.append(u'Incorrect number class-wise development results given [{class_wise:d}/{target:d}]'.format(
                                    class_wise=len(results.get_path('development_dataset.event_based.class_wise')),
                                    target=len(self.class_labels)
                                ))

                            for class_label, class_data in iteritems(results.get_path('development_dataset.event_based.class_wise')):
                                if class_data.get('er') is None:
                                    self.error_log.append(u'Incorrect class-wise development results given for [{class_label:s} / er]'.format(
                                            class_label=class_label
                                    ))

                                if class_data.get('f1') is None:
                                    self.error_log.append(u'Incorrect class-wise development results given for [{class_label:s} / f1]'.format(
                                            class_label=class_label
                                    ))

                        else:
                            self.error_log.append(u'No class_wise development results given')

                    elif task == 'SED_segment':
                        if results.get_path('development_dataset.segment_based.class_wise') is not None:
                            if len(results.get_path('development_dataset.segment_based.class_wise')) != len(self.class_labels):
                                self.error_log.append(u'Incorrect number class-wise development results given [{class_wise:d}/{target:d}]'.format(
                                    class_wise=len(results.get_path('development_dataset.segment_based.class_wise')),
                                    target=len(self.class_labels)
                                ))

                            for class_label, class_data in iteritems(results.get_path('development_dataset.segment_based.class_wise')):
                                if class_data.get('er') is None:
                                    self.error_log.append(u'Incorrect class-wise development results given for [{class_label:s} / er]'.format(
                                            class_label=class_label
                                    ))

                                if class_data.get('f1') is None:
                                    self.error_log.append(u'Incorrect class-wise development results given for [{class_label:s} / f1]'.format(
                                            class_label=class_label
                                    ))

                        else:
                            self.error_log.append(u'No class_wise development results given')

                    elif task == 'task4':
                        pass

            if check_evaluation_dataset:
                # Check evaluation dataset results
                if 'evaluation_dataset' not in results:
                    self.error_log.append(u'No evaluation results given')

                else:
                    if task == 'ASC':
                        if results.get_path('evaluation_dataset.overall') is None:
                            self.error_log.append(u'No evaluation results given')

                        if results.get_path('evaluation_dataset.class_wise') is not None:
                            if len(results.get_path('evaluation_dataset.class_wise')) != len(self.class_labels):
                                self.error_log.append(
                                    u'Incorrect number class-wise evaluation results given [{class_wise:d}/{target:d}]'.format(
                                        class_wise=len(results.get_path('evaluation_dataset.class_wise')),
                                        target=len(self.class_labels)
                                    ))

                            for class_label, class_data in iteritems(results.get_path('evaluation_dataset.class_wise')):
                                if class_data.get('accuracy') is None:
                                    self.error_log.append(
                                        u'Incorrect class-wise evaluation results given for [{class_label:s}]'.format(
                                            class_label=class_label
                                        ))
                        else:
                            self.error_log.append(u'No class_wise development results given')

                    elif task == 'SED_event':
                        if results.get_path('evaluation_dataset.event_based.overall.er') is None:
                            self.error_log.append(u'No evaluation results given [event_based.overall.er]')

                        if results.get_path('evaluation_dataset.event_based.overall.f1') is None:
                            self.error_log.append(u'No evaluation results given [event_based.overall.f1]')

                        if results.get_path('evaluation_dataset.event_based.class_wise') is not None:
                            if len(results.get_path('evaluation_dataset.event_based.class_wise')) != len(self.class_labels):
                                self.error_log.append(
                                    u'Incorrect number class-wise evaluation results given [{class_wise:d}/{target:d}]'.format(
                                        class_wise=len(results.get_path('evaluation_dataset.event_based.class_wise')),
                                        target=len(self.class_labels)
                                    ))

                            for class_label, class_data in iteritems(results.get_path('evaluation_dataset.event_based.class_wise')):
                                if class_data.get('er') is None:
                                    self.error_log.append(
                                        u'Incorrect class-wise evaluation results given for [{class_label:s} / er]'.format(
                                            class_label=class_label
                                        ))

                                if class_data.get('f1') is None:
                                    self.error_log.append(
                                        u'Incorrect class-wise evaluation results given for [{class_label:s} / f1]'.format(
                                            class_label=class_label
                                        ))

                        else:
                            self.error_log.append(u'No class_wise evaluation results given')

                    elif task == 'SED_segment':
                        if results.get_path('evaluation_dataset.segment_based.overall.er') is None:
                            self.error_log.append(u'No evaluation results given [segment_based.overall.er]')

                        if results.get_path('evaluation_dataset.segment_based.overall.f1') is None:
                            self.error_log.append(u'No evaluation results given [segment_based.overall.f1]')

                        if results.get_path('evaluation_dataset.segment_based.class_wise') is not None:
                            if len(results.get_path('evaluation_dataset.segment_based.class_wise')) != len(self.class_labels):
                                self.error_log.append(
                                    u'Incorrect number class-wise evaluation results given [{class_wise:d}/{target:d}]'.format(
                                        class_wise=len(results.get_path('evaluation_dataset.segment_based.class_wise')),
                                        target=len(self.class_labels)
                                    ))

                            for class_label, class_data in iteritems(results.get_path('evaluation_dataset.segment_based.class_wise')):
                                if class_data.get('er') is None:
                                    self.error_log.append(
                                        u'Incorrect class-wise evaluation results given for [{class_label:s} / er]'.format(
                                            class_label=class_label
                                        ))

                                if class_data.get('f1') is None:
                                    self.error_log.append(
                                        u'Incorrect class-wise evaluation results given for [{class_label:s} / f1]'.format(
                                            class_label=class_label
                                        ))

                        else:
                            self.error_log.append(u'No class_wise evaluation results given')

                    elif task == 'task4':
                        pass

        return self

    def system_description(self, meta, style='DCASE2017'):
        """Check system description meta data

        Parameters
        ----------
        meta : dict
            System meta data

        style : str
            Style [DCASE2017, DCASE2016]

        Returns
        -------
        self

        """

        if style == 'DCASE2017':

            if 'acoustic_features' not in meta:
                self.error_log.append('No system.description.acoustic_features field')

            if 'data_augmentation' not in meta:
                self.error_log.append('No system.description.data_augmentation field')

            if 'decision_making' not in meta:
                self.error_log.append('No system.description.decision_making field')

            if 'input_channels' not in meta:
                self.error_log.append('No system.description.input_channels field')

            if 'input_sampling_rate' not in meta:
                self.error_log.append('No system.description.input_sampling_rate field')

            if 'machine_learning_method' not in meta:
                self.error_log.append('No system.description.machine_learning_method field')

            if 'acoustic_features' not in meta or meta['acoustic_features'] is None:
                self.error_log.append('No system.description.features value')

            if 'machine_learning_method' not in meta or meta['machine_learning_method'] is None:
                self.error_log.append('No system.description.machine_learning_method value')

        elif style == 'DCASE2016':
            if 'features' not in meta:
                self.error_log.append('No system.description.features field')

            if 'classifier' not in meta:
                self.error_log.append('No system.description.classifier field')

            if 'input' not in meta:
                self.error_log.append('No system.description.input field')

            if 'preprocessing' not in meta:
                self.error_log.append('No system.description.preprocessing field')

            if 'sampling_rate' not in meta:
                self.error_log.append('No system.description.sampling_rate field')

            if 'training_data' not in meta:
                self.error_log.append('No system.description.training_data field')

        return self

    def system_output(self, output, task=None, allow_placeholder_lines_in_output=None):
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
        self

        """

        if task is None:
            task = self.task

        if allow_placeholder_lines_in_output is None:
            allow_placeholder_lines_in_output = self.allow_placeholder_lines_in_output

        if len(output.unique_files) != self.file_count:
            self.error_log.append(u'Wrong number of files in output ({current:d}/{target:d})'.format(
                current=len(output.unique_files),
                target=self.file_count,
            ))

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
            self.error_log.append(u'Wrong number of fields [{field_count:d}]'.format(
                field_count=len(invalid_item)
            ))

        if invalid_labels:
            self.error_log.append(u'Invalid labels found [{invalid_labels:s}]'.format(
                invalid_labels=', '.join(invalid_labels),
            ))

        return self

