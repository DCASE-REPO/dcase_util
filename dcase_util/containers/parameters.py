#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
from six import iteritems

import os
import sys
import hashlib
import json
import copy
import numpy
import itertools
import platform

from dcase_util.containers import DictContainer, ListDictContainer, OneToOneMappingContainer
from dcase_util.utils import VectorRecipeParser, Path, ApplicationPaths, FileFormat


class ParameterContainer(DictContainer):
    """Parameter container class for parameters, inherited from DictContainer class."""
    valid_formats = [FileFormat.YAML]  #: Valid file formats


class AppParameterContainer(ParameterContainer):
    """Parameter container class for application parameters, inherited from ParameterContainer."""
    def __init__(self, data=None, app_base=None, application_directory_parameter_filename='parameters.yaml', **kwargs):
        """Constructor

        Parameters
        ----------
        data : dict
            Dictionary to initialize container

        app_base : str
            Absolute path to the project root

        section_process_order : list, optional
            Parameter section processing order. Given dict is used to override internal default list.

        path_structure : dict of lists, optional
            Defines how paths are created, section hash is used to create unique folder names. Given dict is used to
            override internal default list.

        method_dependencies : dict of dicts, optional
            Given dict is used to override internal default list.

        magic_field : dict, optional
            Dict of field names for specific tasks. Given dict is used to override internal default list.

        non_hashable_fields : list, optional
            List of fields skipped when parameter hash for the section is calculated. Given list is used to override
            internal default list.

        control_sections : list, optional
            List of top level sections used for framework control, for these section no hash is calculated. Given list
            is used to override internal default list.

        """

        # Run DictContainer init
        DictContainer.__init__(self, data, **kwargs)

        super(ParameterContainer, self).__init__(**kwargs)

        # Defaults
        # Map for field names
        self.default_field_labels = OneToOneMappingContainer({
            'DEFAULT-PARAMETERS': 'defaults',
            'SET-LIST': 'sets',
            'SET-ID': 'set_id',
            'ACTIVE-SET': 'active_set',
            'PARAMETERS': 'parameters',
            'LABEL': 'method',
            'RECIPE': 'recipe',
            'STACKING_RECIPE': 'stacking_recipe',
            'BASE': 'base',
            'METHOD_PARAMETERS': 'method_parameters',
            'DEPENDENCY_PARAMETERS': 'dependency_parameters',
            'DEPENDENCY_LABEL': 'dependency_method',
        })

        # Map for Section names
        self.default_section_labels = OneToOneMappingContainer({
            'GENERAL': 'general',
            'PATH': 'path',
            'APPLICATION_PATHS': 'application',
            'EXTERNAL_PATHS': 'external',
            'FLOW': 'flow',
            'LOGGING': 'logging',
        })

        # Section processing order
        self.default_section_process_order = [
            'FLOW',
            'GENERAL',
            'LOGGING',
            'PATH',
        ]

        # Define how paths are constructed from section hashes
        self.default_path_structure = DictContainer({})

        self.default_method_dependencies = DictContainer({})

        # Fields to be skipped when parameter hash is calculated
        self.default_non_hashable_fields = [
            '_hash',
            'verbose',
            'print_system_progress',
            'log_system_parameters',
            'log_system_progress',
            'log_learner_status',
            'show_model_information',
            'use_ascii_progress_bar',
            'label',
            'active_scenes',
            'active_events',
            'plotting_rate',
            'focus_span',
            'output_format',
        ]

        self.default_non_hashable_sections = [
            'FLOW',
            'PATH',
            'LOGGING',
            'GENERAL'
        ]

        # Mark container non-processed, allow processing only once
        self.processed = False

        # Application base path
        if app_base is not None:
            self.app_base = app_base
        else:
            self.app_base = os.path.abspath(os.path.dirname(sys.argv[0]))
            if os.path.split(self.app_base)[1] == 'src':
                # If we are in 'src' folder remove one level
                self.app_base = os.path.join(os.path.split(self.app_base)[0])

        self.application_directory_parameter_filename = application_directory_parameter_filename

        self.field_labels = self.default_field_labels
        self.section_labels = self.default_section_labels
        self.section_process_order = self.default_section_process_order
        self.path_structure = self.default_path_structure
        self.method_dependencies = self.default_method_dependencies
        self.non_hashable_sections = self.default_non_hashable_sections

        # Reset container and inject parameters
        self.reset(**kwargs)

    def reset(self, field_labels=None, section_labels=None, section_process_order=None, path_structure=None,
              method_dependencies=None, non_hashable_fields=None, non_hashable_sections=None, **kwargs):

        # Mark container non-processed, allow processing only once
        self.processed = False

        # Map for field names
        self.field_labels = self.default_field_labels
        if field_labels is not None:
            self.field_labels.update(field_labels)

        # Map for Section names
        self.section_labels = self.default_section_labels
        if section_labels is not None:
            self.section_labels.update(section_labels)

        # Define section processing order
        self.section_process_order = self.default_section_process_order
        if section_process_order is not None:
            self.section_process_order.update(section_process_order)

        # Translate section_process_order
        for order_id, section_label in enumerate(self.section_process_order):
            if section_label in self.section_labels:
                self.section_process_order[order_id] = self.section_labels[section_label]

        # Define how paths are constructed from section hashes
        self.path_structure = self.default_path_structure
        if path_structure is not None:
            self.path_structure.update(path_structure)

        # Translate path_structure
        for key, structure in iteritems(self.path_structure):
            for part_id, part in enumerate(structure):
                split = part.split('.')
                # Translate only first section level
                if split[0] in self.section_labels:
                    split[0] = self.section_labels[split[0]]
                structure[part_id] = '.'.join(split)
            self.path_structure[key] = structure

            # translate key
            if key in self.section_labels:
                new_key = self.section_labels[key]
                self.path_structure[new_key] = self.path_structure.pop(key)

        # Method dependencies map
        self.method_dependencies = self.default_method_dependencies
        if method_dependencies is not None:
            self.method_dependencies.update(method_dependencies)

        # Fields to be skipped when parameter hash is calculated
        self.non_hashable_fields = self.default_non_hashable_fields
        if non_hashable_fields is not None:
            self.non_hashable_fields.update(non_hashable_fields)

        # Parameters sections which will not be included in the master parameter hash
        self.non_hashable_sections = self.default_non_hashable_sections
        if non_hashable_sections is not None:
            self.non_hashable_sections.update(non_hashable_sections)

        # Translate non_hashable_sections
        for order_id, section_label in enumerate(self.non_hashable_sections):
            if section_label in self.section_labels:
                self.non_hashable_sections[order_id] = self.section_labels[section_label]

    def process(self, create_paths=True, create_parameter_hints=True):
        """Process parameters

        Parameters
        ----------
        create_paths : bool
            Create paths

        create_parameter_hints : bool
            Create parameters files to all data folders

        Raises
        ------
        ValueError:
            No valid active set given

        Returns
        -------
        self

        """

        # Check for empty parameter container
        if len(self) == 0:
            message = '{name}: Parameter container empty, cannot be process'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise IOError(message)

        # Process only once
        if not self.processed:
            # Translate non hashable section names
            for section_id, section in enumerate(self.non_hashable_sections):
                if section in self.field_labels:
                    self.non_hashable_sections[section_id] = self.field_labels[section]

            if (self.field_labels['DEFAULT-PARAMETERS'] in self and
               self.field_labels['SET-LIST'] in self and
               self.field_labels['ACTIVE-SET'] in self):
                # Process active-set, set-list, default structured parameters

                # Get default parameters
                default_params = copy.deepcopy(self[self.field_labels['DEFAULT-PARAMETERS']])

                # Active set ID
                active_set_id = self[self.field_labels['ACTIVE-SET']]

                active_set = ListDictContainer(self[self.field_labels['SET-LIST']]).search(
                    key=self.field_labels['SET-ID'],
                    value=active_set_id
                )

                if not active_set:
                    message = '{name}: No valid active set given [{set_name}]'.format(
                        name=self.__class__.__name__,
                        set_name=active_set_id
                    )

                    self.logger.exception(message)
                    raise ValueError(message)

                # Empty current content
                dict.clear(self)

                # Insert default parameters
                dict.update(self, default_params)
                self[self.field_labels['ACTIVE-SET']] = active_set_id

                # Merge override active parameter set on top of default parameters
                self.merge(override=active_set)

            elif self.field_labels['DEFAULT-PARAMETERS'] in self:
                # Only default parameter set is given, make it only one.
                default_params = copy.deepcopy(self[self.field_labels['DEFAULT-PARAMETERS']])
                dict.clear(self)
                dict.update(self, default_params)

            # Get processing order for sections
            section_list = []
            for section in self.section_process_order + list(set(list(self.keys())) - set(self.section_process_order)):
                if section in self:
                    section_list.append(section)

            # Parameter processing starts

            # Convert all main level sections to DictContainers
            self._convert_main_level_to_containers()

            # Prepare paths
            self._prepare_paths()

            # 1. Process parameters
            for section in section_list:
                # Reverse translated section name
                section_name = self.section_labels.flipped.map(section)

                # Get processing function
                field_process_func = getattr(self, '_process_{}'.format(section_name), None)

                if field_process_func is not None:
                    # Call processing function if it exists
                    field_process_func()

                # Call processing function to method section related to the current section
                section_method_parameters = section + '_' + self.field_labels['METHOD_PARAMETERS']

                if section in self and isinstance(self[section], dict) and section_method_parameters in self:
                    if self.field_labels['LABEL'] in self[section] or self.field_labels['RECIPE'] in self[section]:
                        field_process_parameters_func = getattr(
                            self,
                            '_process_{SECTION_NAME}_METHOD_PARAMETERS'.format(SECTION_NAME=section_name),
                            None
                        )

                        if field_process_parameters_func is not None:
                            field_process_parameters_func()

            # 2. Add parameter hash to methods
            self._add_hash_to_method_parameters()

            # 3. Parse recipes
            recipe_paths = self.get_leaf_path_list(target_field_endswith=self.field_labels['RECIPE'])
            for recipe_path in recipe_paths:
                self.set_path(
                    path=recipe_path,
                    new_value=VectorRecipeParser().parse(recipe=self.get_path(path=recipe_path))
                )

            # 4. Process methods
            for section in section_list:
                self._process_method_parameters(section=section)

            # 5. Inject dependencies
            for section in section_list:
                section_name = self.section_labels.flipped.map(section)
                if section_name:
                    # Apply only named sections
                    if self.get_path_translated(path=[section, 'PARAMETERS']):
                        for key, item in iteritems(self.get_path_translated(path=[section, 'PARAMETERS'])):

                            if self.method_dependencies.get_path([section_name, key]):
                                dependency_path = self._translated_path(
                                    self.method_dependencies.get_path([section_name, key]).split('.')
                                )

                                if len(dependency_path) == 1:
                                    section_method_parameters = section + '_' + self.field_labels['METHOD_PARAMETERS']

                                    item[self.field_labels['DEPENDENCY_PARAMETERS']] = copy.deepcopy(
                                        self.get_path([section_method_parameters] + dependency_path[1:])
                                    )

                                    item[self.field_labels['DEPENDENCY_LABEL']] = dependency_path[-1]

                                elif len(dependency_path) == 2:
                                    section_method_parameters = dependency_path[0] + '_' + self.field_labels['METHOD_PARAMETERS']

                                    item[self.field_labels['DEPENDENCY_PARAMETERS']] = copy.deepcopy(
                                        self.get_path([section_method_parameters] + dependency_path[1:])
                                    )

                                    item[self.field_labels['DEPENDENCY_LABEL']] = dependency_path[-1]

            # 6. Add hash
            self._add_hash_to_main_parameters()
            self._add_main_hash()

            # 7. Post process paths
            self._process_application_paths(
                create_paths=create_paths,
                create_parameter_hints=create_parameter_hints
            )

            self.processed = True

            # 8. Clean up
            # self._clean_unused_parameters()

        return self

    def get_path_translated(self, path):
        """Get data with path, path can contain string constants which will be translated.

        Parameters
        ----------
        path : list of str
            Path parts

        Returns
        -------
        dict

        """

        return self.get_path(path=self._translated_path(path))

    def set_path_translated(self, path, new_value):
        """Set data with path, path can contain string constants which will be translated.

        Parameters
        ----------
        path : list of str
            Path parts

        new_value : various
            Value to be set

        Returns
        -------
        None

        """

        return self.set_path(path=self._translated_path(path), new_value=new_value)

    def override(self, override):
        """Override container content recursively.

        Parameters
        ----------
        override : dict, str
            Depending type following is done:

            - If dict given, this is used directly to override parameters in the container.
            - If str is given which is a filename of existing file on disk, parameter file is loaded and it is used to override container parameters
            - If str is given which contains JSON formatted parameters, content is used to override container parameters

        Raises
        ------
        ImportError:
            JSON import failed
        ValueError:
            Not JSON formatted string given

        Returns
        -------
        self

        """

        if isinstance(override, dict):
            self.merge(override=override)

        elif isinstance(override, str) and os.path.isfile(override):
            self.merge(override=ParameterContainer(filename=override).load())

        elif isinstance(override, str):
            try:
                try:
                    import ujson as json

                except ImportError:
                    try:
                        import json
                    except ImportError:
                        message = '{name}: Unable to import json module'.format(
                            name=self.__class__.__name__
                        )

                        self.logger.exception(message)
                        raise ImportError(message)

                self.merge(override=json.loads(override))

            except:
                message = '{name}: Not JSON formatted string given'.format(
                    name=self.__class__.__name__
                )

                self.logger.exception(message)
                raise ValueError(message)

        return self

    def _process_method_parameters(self, section):
        """Process methods and recipes in the section

        Processing rules for fields:

        - "method" => search for parameters from [section]_method_parameters -section
        - "recipe" => parse recipe and search for parameters from [section]_method_parameters -section
        - "\*recipe" => parse recipe

        Parameters
        ----------
        section : str
            Section name

        Raises
        ------
        ValueError:
            Invalid method for parameter field

        Returns
        -------
        self

        """

        if section in self and self[section] and isinstance(self[section], dict):
            # Inject method parameters
            section_method_parameters = section + '_' + self.field_labels['METHOD_PARAMETERS']
            if self.field_labels['LABEL'] in self[section]:
                if (section_method_parameters in self and
                   self[section][self.field_labels['LABEL']] in self[section_method_parameters]):

                    self[section][self.field_labels['PARAMETERS']] = copy.deepcopy(
                        self[section_method_parameters][self[section][self.field_labels['LABEL']]]
                    )

                else:
                    message = '{name}: Invalid method for parameter field, {field}->method={method}'.format(
                        name=self.__class__.__name__,
                        field=section,
                        method=self[section][self.field_labels['LABEL']]
                    )

                    self.logger.exception(message)
                    raise ValueError(message)

            # Inject parameters based on recipes
            if self.field_labels['RECIPE'] in self[section]:
                self.set_path_translated(path=[section, 'PARAMETERS'], new_value={})

                for item in self.get_path_translated(path=[section, 'RECIPE']):

                    if self.field_labels['LABEL'] in item:
                        label = item[self.field_labels['LABEL']]

                    elif 'label' in item:
                        label = item['label']

                    parameters = self.get_path_translated(path=[section_method_parameters, label])

                    if parameters:
                        self.set_path_translated(
                            path=[section, 'PARAMETERS', label],
                            new_value=parameters
                        )

                    else:
                        message = '{name}: Cannot find any parameters for the method in the recipe field, {field}->recipe={method}'.format(
                            name=self.__class__.__name__,
                            field=section,
                            method=label
                        )

                        self.logger.exception(message)
                        raise ValueError(message)

        return self

    def _translated_path(self, path):
        """Path translation, defined section_label is used as translation map.

        Parameters
        ----------
        path : list of str
            Path parts

        Returns
        -------
        list of str
            Path parts with translation

        """

        translated_path = []
        for p in path:
            if p in self.section_labels:
                translated_path.append(self.section_labels.map(p))

            elif p in self.field_labels:
                translated_path.append(self.field_labels.map(p))

            else:
                translated_path.append(p)

        return translated_path

    def _prepare_paths(self):
        """Prepare paths"""
        if self.section_labels['PATH'] in self:
            if platform.system() == 'Windows':
                # Translate separators if in Windows
                for path_key, path in iteritems(self.get_path_translated(path=['PATH'])):
                    if isinstance(path, str):
                        self.set_path_translated(path=['PATH', path_key], new_value=Path(path).posix_to_nt())

                    elif isinstance(path, dict):
                        for path_key_sub, path_sub in iteritems(self.get_path_translated(path=['PATH', path_key])):
                            if isinstance(path_sub, str):
                                self.set_path_translated(
                                    path=['PATH', path_key, path_key_sub],
                                    new_value=Path(path_sub).posix_to_nt())

            # Translate paths to be absolute
            if self.get_path_translated(path=['PATH', 'APPLICATION_PATHS']):
                # Container has application paths

                if self.get_path_translated(path=['PATH', 'APPLICATION_PATHS', 'BASE']):
                    # Container has application base path
                    base_path = self.get_path_translated(path=['PATH', 'APPLICATION_PATHS', 'BASE'])

                    if not os.path.isabs(base_path):
                        base_path = os.path.join(self.app_base, base_path)
                        self.set_path_translated(
                            path=['PATH', 'APPLICATION_PATHS', 'BASE'],
                            new_value=base_path
                        )
                else:
                    # No base path given, use main application base
                    base_path = self.app_base

                # Extend rest of the application paths
                for path_key, path in iteritems(self.get_path_translated(path=['PATH', 'APPLICATION_PATHS'])):
                    if path_key is not self.field_labels['BASE'] and not os.path.isabs(path):
                        path = os.path.join(base_path, path)
                        self.set_path_translated(
                            path=['PATH', 'APPLICATION_PATHS', path_key],
                            new_value=path
                        )

            if self.get_path_translated(path=['PATH', 'EXTERNAL_PATHS']):
                # Container has external paths
                for path_key, path in iteritems(self.get_path_translated(path=['PATH', 'EXTERNAL_PATHS'])):
                    if not os.path.isabs(path):
                        path = os.path.join(self.app_base, path)
                        self.set_path_translated(
                            path=['PATH', 'EXTERNAL_PATHS', path_key],
                            new_value=path
                        )

    def _process_application_paths(self, create_paths=True, create_parameter_hints=True):
        """Process application paths"""
        # Make sure extended paths exists before saving parameters in them
        if create_paths:
            # Create paths
            paths = self.get_path_translated(path=['PATH'])
            if paths:
                for path_key, path in iteritems(paths):
                    if isinstance(path, str):
                        Path().create(path)
                    elif isinstance(path, dict):
                        for path_key_sub, path_sub in iteritems(self.get_path_translated(path=['PATH', path_key])):
                            if isinstance(path_sub, str):
                                Path().create(path_sub)

        # Check path_structure
        app_paths = self.get_path_translated(path=['PATH', 'APPLICATION_PATHS'])
        if app_paths:
            for field, structure in iteritems(self.path_structure):
                if field in app_paths:
                    if self.field_labels['BASE'] in app_paths:
                        path_base = os.path.join(
                            app_paths[self.field_labels['BASE']],
                            app_paths[field]
                        )
                    else:
                        path_base = os.path.join(
                            self.app_base,
                            app_paths[field]
                        )

                    # Generate full path with parameter hashes
                    path = ApplicationPaths(parameter_container=self).generate(
                        path_base=path_base,
                        structure=structure
                    )

                    # Check for path limitations
                    if platform.system() == 'Windows':
                        if isinstance(path, dict):
                            for key, p in iteritems(path):
                                if len(p) >= 255:
                                    message = '{name}: Path potentially exceeds Windows path length limit (255) [{path}]'.format(
                                        name=self.__class__.__name__,
                                        path=p
                                    )
                                    self.logger.warning(message)

                    # Create directories
                    if create_paths:
                        Path().create(paths=path)

                    # Create parameter hints
                    if create_parameter_hints:
                        ApplicationPaths(parameter_container=self).save_parameters_to_path(
                            path_base=path_base,
                            structure=structure,
                            parameter_filename=self.application_directory_parameter_filename
                        )

                    # Update path in the container
                    self.set_path_translated(
                        path=['PATH', 'APPLICATION_PATHS', field],
                        new_value=path
                    )

    def _add_hash_to_main_parameters(self):
        """Add has to the main sections."""
        for field, params in iteritems(self):
            if isinstance(params, dict):
                if field not in self.non_hashable_sections and self[field]:
                    self[field]['_hash'] = self.get_hash(data=self[field])

    def _add_hash_to_method_parameters(self):
        """Add has to the method parameter sections."""
        for field in self:
            if field.endswith('_method_parameters'):
                for key, params in iteritems(self[field]):
                    if params and isinstance(params, dict):
                        params['_hash'] = self.get_hash(data=params)

    def _add_main_hash(self):
        """Add main level hash."""
        data = {}
        for field, params in iteritems(self):
            if isinstance(params, dict):
                if field not in self.non_hashable_sections and self[field]:
                    data[field] = self.get_hash(data=self[field])
        self['_hash'] = self.get_hash(data=data)

    def _after_load(self, to_return=None):
        """Method triggered after parameters have been loaded."""
        self.processed = False

    def _clean_unused_parameters(self):
        """Remove unused parameters from the parameter dictionary."""
        for field in list(self.keys()):
            if field.endswith('_method_parameters'):
                del self[field]

    def _convert_main_level_to_containers(self):
        """Convert main level sections to DictContainers."""
        for key, item in iteritems(self):
            if isinstance(item, dict) and self.field_labels['PARAMETERS'] in item:
                item[self.field_labels['PARAMETERS']] = DictContainer(item[self.field_labels['PARAMETERS']])
            if isinstance(item, dict):
                self[key] = DictContainer(item)


class DCASEAppParameterContainer(AppParameterContainer):
    """Parameter container class for DCASE application parameter files, inherited from AppParameterContainer."""
    def __init__(self, *args, **kwargs):
        super(DCASEAppParameterContainer, self).__init__(*args, **kwargs)

        self.default_section_labels.update({
            'DATASET': 'dataset',
            'DATASET_METHOD_PARAMETERS': 'dataset_method_parameters',
            'FEATURE_EXTRACTOR': 'feature_extractor',
            'FEATURE_EXTRACTOR_METHOD_PARAMETERS': 'feature_extractor_method_parameters',
            'FEATURE_STACKER': 'feature_stacker',
            'FEATURE_STACKER_METHOD_PARAMETERS': 'feature_stacker_method_parameters',
            'FEATURE_NORMALIZER': 'feature_normalizer',
            'FEATURE_NORMALIZER_PARAMETERS': 'feature_normalizer_parameters',
            'FEATURE_AGGREGATOR': 'feature_aggregator',
            'FEATURE_AGGREGATOR_PARAMETERS': 'feature_aggregator_parameters',
            'LEARNER': 'learner',
            'LEARNER_METHOD_PARAMETERS': 'learner_method_parameters',
            'RECOGNIZER': 'recognizer',
            'RECOGNIZER_METHOD_PARAMETERS': 'recognizer_method_parameters',
            'EVALUATOR': 'evaluator'
        })

        # Section processing order
        self.default_section_process_order += [
            'DATASET',
            'DATASET_METHOD_PARAMETERS',
            'FEATURE_EXTRACTOR',
            'FEATURE_EXTRACTOR_METHOD_PARAMETERS',
            'FEATURE_STACKER',
            'FEATURE_STACKER_METHOD_PARAMETERS',
            'FEATURE_NORMALIZER',
            'FEATURE_NORMALIZER_PARAMETERS',
            'FEATURE_AGGREGATOR',
            'FEATURE_AGGREGATOR_PARAMETERS',
            'LEARNER',
            'RECOGNIZER',
            'LEARNER_METHOD_PARAMETERS',
            'RECOGNIZER_METHOD_PARAMETERS',
            'EVALUATOR'
        ]

        self.default_path_structure.update({
            'FEATURE_EXTRACTOR': [
                'FEATURE_EXTRACTOR.parameters.*'
            ],
            'FEATURE_NORMALIZER': [
                'FEATURE_EXTRACTOR.parameters.*'
            ],
            'LEARNER': [
                'FEATURE_EXTRACTOR',
                'FEATURE_STACKER',
                'FEATURE_NORMALIZER',
                'FEATURE_AGGREGATOR',
                'LEARNER'
            ],
            'RECOGNIZER': [
                'FEATURE_EXTRACTOR',
                'FEATURE_STACKER',
                'FEATURE_NORMALIZER',
                'FEATURE_AGGREGATOR',
                'LEARNER',
                'RECOGNIZER'
            ],
            'EVALUATOR': [
            ]
        })

        self.default_method_dependencies.update({
            'FEATURE_EXTRACTOR': {
                'mel': None,
                'mfcc': None,
                'mfcc_delta': 'FEATURE_EXTRACTOR.mfcc',
                'mfcc_acceleration': 'FEATURE_EXTRACTOR.mfcc',
            }
        })

        self.default_non_hashable_sections += [
            'EVALUATOR'
        ]

        self.reset(**kwargs)

    def _process_LOGGING(self):
        """Process LOGGING section."""

        handlers = self.get_path_translated(path=['LOGGING', 'parameters', 'handlers'])
        if handlers:
            for handler_name, handler_data in iteritems(handlers):
                if 'filename' in handler_data:
                    if self.get_path(path=self.section_labels['PATH'] + '.'+self.section_labels['EXTERNAL_PATHS'] + '.logs'):
                        handler_data['filename'] = os.path.join(
                            self.get_path_translated(path=['PATH', 'EXTERNAL_PATHS', 'logs']),
                            handler_data['filename']
                        )

                    elif self.get_path(
                            path=self.section_labels['PATH'] + '.'+self.section_labels['APPLICATION_PATHS'] + '.logs'):
                        handler_data['filename'] = os.path.join(
                            self.get_path_translated(path=['PATH', 'APPLICATION_PATHS', 'logs']),
                            handler_data['filename']
                        )

    def _process_FEATURE_EXTRACTOR(self):
        """Process FEATURE_EXTRACTION section."""

        if not self.get_path_translated(path=['FEATURE_EXTRACTOR', 'RECIPE']) and self.get_path_translated(path=['FEATURE_STACKER', 'STACKING_RECIPE']):
            self.set_path_translated(
                path=['FEATURE_EXTRACTOR', 'RECIPE'],
                new_value=self.get_path_translated(path=['FEATURE_STACKER', 'STACKING_RECIPE']))

        # Calculate window length in samples
        if self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds']) and self.get_path_translated(path=['FEATURE_EXTRACTOR', 'fs']):
            self.set_path_translated(
                path=['FEATURE_EXTRACTOR', 'win_length_samples'],
                new_value=int(self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds']) * self.get_path_translated(path=['FEATURE_EXTRACTOR', 'fs']))
            )

        # Calculate hop length in samples
        if self.get_path_translated(path=['FEATURE_EXTRACTOR', 'hop_length_seconds']) and self.get_path_translated(path=['FEATURE_EXTRACTOR', 'fs']):
            self.set_path_translated(
                path=['FEATURE_EXTRACTOR', 'hop_length_samples'],
                new_value=int(self.get_path_translated(path=['FEATURE_EXTRACTOR', 'hop_length_seconds']) * self.get_path_translated(path=['FEATURE_EXTRACTOR', 'fs']))
            )

    def _process_FEATURE_NORMALIZER(self):
        """Process FEATURE_NORMALIZER section."""

        if self.get_path_translated(path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                path=['FEATURE_NORMALIZER', 'scene_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'scene_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                path=['FEATURE_NORMALIZER', 'active_scenes'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_scenes'])
            )

        if self.get_path_translated(path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                path=['FEATURE_NORMALIZER', 'event_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'event_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_events']):
            self.set_path_translated(
                path=['FEATURE_NORMALIZER', 'active_events'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_events'])
            )

    def _process_FEATURE_EXTRACTOR_METHOD_PARAMETERS(self):
        """Process FEATURE_EXTRACTOR_METHOD_PARAMETERS section."""

        method_parameter_field = self.section_labels['FEATURE_EXTRACTOR'] + '_' + self.field_labels['METHOD_PARAMETERS']
        if method_parameter_field in self:
            # Change None feature parameter sections into empty dicts
            for method in list(self[method_parameter_field].keys()):
                if self[method_parameter_field][method] is None:
                    self[method_parameter_field][method] = {}

            for method, data in iteritems(self[method_parameter_field]):
                data['method'] = method

                # Copy general parameters
                if self.get_path_translated(path=['FEATURE_EXTRACTOR', 'fs']):
                    data['fs'] = self.get_path_translated(path=['FEATURE_EXTRACTOR', 'fs'])

                if self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds']):
                    data['win_length_seconds'] = self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds'])
                if self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_samples']):
                    data['win_length_samples'] = self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_samples'])

                if self.get_path_translated(path=['FEATURE_EXTRACTOR', 'hop_length_seconds']):
                    data['hop_length_seconds'] = self.get_path_translated(path=['FEATURE_EXTRACTOR', 'hop_length_seconds'])
                if self.get_path_translated(path=['FEATURE_EXTRACTOR', 'hop_length_samples']):
                    data['hop_length_samples'] = self.get_path_translated(path=['FEATURE_EXTRACTOR', 'hop_length_samples'])

    def _process_FEATURE_AGGREGATOR(self):
        """Process FEATURE_AGGREGATOR section."""

        if self.get_path_translated(path=['FEATURE_AGGREGATOR', 'win_length_seconds']) and self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds']):
            self.set_path_translated(
                path=['FEATURE_AGGREGATOR', 'win_length_frames'],
                new_value=int(numpy.ceil(self.get_path_translated(path=['FEATURE_AGGREGATOR', 'win_length_seconds']) / float(self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds']))))
            )

        if self.get_path_translated(path=['FEATURE_AGGREGATOR', 'hop_length_seconds']) and self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds']):
            self.set_path_translated(
                path=['FEATURE_AGGREGATOR', 'hop_length_frames'],
                new_value=int(numpy.ceil(self.get_path_translated(path=['FEATURE_AGGREGATOR', 'hop_length_seconds']) / float(self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds']))))
            )

    def _process_LEARNER(self):
        """Process LEARNER section."""

        # Process window length and hop length
        win_length_seconds = self.get_path_translated(path=['FEATURE_EXTRACTOR', 'win_length_seconds'])
        hop_length_seconds = self.get_path_translated(path=['FEATURE_EXTRACTOR', 'hop_length_seconds'])

        if self.get_path_translated(path=['FEATURE_AGGREGATOR', 'enable']):
            win_length_seconds = self.get_path_translated(path=['FEATURE_AGGREGATOR', 'win_length_seconds'])
            hop_length_seconds = self.get_path_translated(path=['FEATURE_AGGREGATOR', 'hop_length_seconds'])

        if win_length_seconds:
            self.set_path_translated(
                path=['LEARNER', 'win_length_seconds'],
                new_value=float(win_length_seconds)
            )

        if hop_length_seconds:
            self.set_path_translated(
                path=['LEARNER', 'hop_length_seconds'],
                new_value=float(hop_length_seconds)
            )

        # Process specifiers
        if self.get_path_translated(path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                path=['LEARNER', 'scene_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'scene_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                path=['LEARNER', 'active_scenes'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_scenes'])
            )

        if self.get_path_translated(path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                path=['LEARNER', 'event_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'event_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_events']):
            self.set_path_translated(
                path=['LEARNER', 'active_events'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_events'])
            )

    def _process_LEARNER_METHOD_PARAMETERS(self):
        """Process LEARNER_METHOD_PARAMETERS section."""

        method_parameter_field = self.section_labels['LEARNER'] + '_' + self.field_labels['METHOD_PARAMETERS']

        if method_parameter_field in self:
            for method, data in iteritems(self[method_parameter_field]):
                data = DictContainer(data)
                if data.get_path('training.epoch_processing.enable') and not data.get_path('training.epoch_processing.recognizer'):
                    data['training']['epoch_processing']['recognizer'] = self.get_path_translated(path=['RECOGNIZER'])

    def _process_RECOGNIZER(self):
        """Process RECOGNIZER section."""

        # Process specifiers
        if self.get_path_translated(path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                path=['RECOGNIZER', 'scene_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'scene_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                path=['RECOGNIZER', 'active_scenes'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_scenes'])
            )

        if self.get_path_translated(path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                path=['RECOGNIZER', 'event_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'event_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_events']):
            self.set_path_translated(
                path=['RECOGNIZER', 'active_events'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_events'])
            )

        # Inject frame accumulation parameters
        if (self.get_path_translated(path=['RECOGNIZER', 'frame_accumulation', 'enable']) and
                self.get_path_translated(path=['RECOGNIZER', 'frame_accumulation', 'window_length_seconds'])):
            self.set_path_translated(
                path=['RECOGNIZER', 'frame_accumulation', 'window_length_frames'],
                new_value=int(self.get_path_translated(path=['RECOGNIZER', 'frame_accumulation', 'window_length_seconds']) / float(self.get_path_translated(path=['LEARNER', 'hop_length_seconds'])))
            )

        # Inject event activity processing parameters
        if self.get_path_translated(path=['RECOGNIZER', 'event_activity_processing', 'enable']) and self.get_path_translated(path=['RECOGNIZER', 'event_activity_processing', 'window_length_seconds']):

            self.set_path_translated(
                path=['RECOGNIZER', 'event_activity_processing', 'window_length_frames'],
                new_value=int(self.get_path_translated(path=['RECOGNIZER', 'event_activity_processing', 'window_length_seconds']) / float(self.get_path_translated(path=['LEARNER', 'hop_length_seconds'])))
            )

    def _process_EVALUATOR(self):
        """Process EVALUATOR section."""

        # Process specifiers
        if self.get_path_translated(path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                path=['EVALUATOR', 'scene_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'scene_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                path=['EVALUATOR', 'active_scenes'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_scenes'])
            )

        if self.get_path_translated(path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                path=['EVALUATOR', 'event_handling'],
                new_value=self.get_path_translated(path=['GENERAL', 'event_handling'])
            )

        if self.get_path_translated(path=['GENERAL', 'active_events']):
            self.set_path_translated(
                path=['EVALUATOR', 'active_events'],
                new_value=self.get_path_translated(path=['GENERAL', 'active_events'])
            )


class ParameterListContainer(ListDictContainer):
    """Parameter list container, inherited from ListDictContainer."""
    valid_formats = ['yaml']  #: Valid file formats

