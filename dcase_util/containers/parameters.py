#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
from six import iteritems

import os
import sys
import copy
import numpy
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
            Default value None

        app_base : str
            Absolute path to the project root
            Default value None

        section_process_order : list, optional
            Parameter section processing order. Given dict is used to override internal default list.
            Default value 'parameters.yaml'

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
            'CHAIN': 'chain',
            'STACKING_RECIPE': 'stacking_recipe',
            'BASE': 'base',
            'ENABLE': 'enable',
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

    def reset(self,
              field_labels=None,
              section_labels=None, section_process_order=None,
              path_structure=None,
              method_dependencies=None,
              non_hashable_fields=None, non_hashable_sections=None, **kwargs):

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
        path_structure_tmp = copy.deepcopy(self.path_structure)
        for key, structure in iteritems(path_structure_tmp):
            for part_id, part in enumerate(structure):
                split = part.split('.')

                # Translate two first levels
                # First level with section_labels
                if split[0] in self.section_labels:
                    split[0] = self.section_labels[split[0]]

                # Second level with field_labels
                if len(split) > 1 and split[1] in self.field_labels:
                    split[1] = self.field_labels[split[1]]

                structure[part_id] = '.'.join(split)

            self.path_structure[key] = structure

            # Translate key
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
            Default value True

        create_parameter_hints : bool
            Create parameters files to all data folders
            Default value True

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

            if self.field_labels['SET-LIST'] in self:
                for set_id, set_defined_parameters in enumerate(self[self.field_labels['SET-LIST']]):
                    # Get default parameters
                    set_params = DictContainer(copy.deepcopy(self[self.field_labels['DEFAULT-PARAMETERS']]))
                    set_params.merge(override=set_defined_parameters)
                    self.process_set(
                        parameters=set_params,
                        create_paths=create_paths,
                        create_parameter_hints=create_parameter_hints
                    )

                    self[self.field_labels['SET-LIST']][set_id] = set_params

            if (self.field_labels['DEFAULT-PARAMETERS'] in self and
               self.field_labels['SET-LIST'] in self and
               self.field_labels['ACTIVE-SET'] in self):
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

                self.merge(override=active_set)

            elif self.field_labels['DEFAULT-PARAMETERS'] in self:
                # Only default parameter set is given, make it only one.
                self.merge(
                    override=copy.deepcopy(self[self.field_labels['DEFAULT-PARAMETERS']])
                )

            else:
                # No sets used
                self.process_set(
                    parameters=self,
                    create_paths=create_paths,
                    create_parameter_hints=create_parameter_hints
                )

            self.processed = True

            # 8. Clean up
            # self._clean_unused_parameters()

        return self

    def process_set(self, parameters, create_paths=True, create_parameter_hints=True):
        """Process parameter set

        Parameters
        ----------
        parameters : dict
            Dictionary to process

        create_paths : bool
            Create paths
            Default value True

        create_parameter_hints : bool
            Create parameters files to all data folders
            Default value True

        Returns
        -------
        self

        """

        # Get processing order for sections
        section_list = []
        for section in self.section_process_order + list(set(list(parameters.keys())) - set(self.section_process_order)):
            if section in parameters:
                section_list.append(section)

        # Convert all main level sections to DictContainers
        self._convert_main_level_to_containers(
            parameters=parameters
        )

        # Prepare paths
        self._prepare_paths(
            parameters=parameters
        )

        # 1. Process parameters
        for section in section_list:
            # Reverse translated section name
            section_name = self.section_labels.flipped.map(section)

            # Get processing function
            field_process_func = getattr(
                self,
                '_process_{SECTION_NAME}'.format(SECTION_NAME=section_name),
                None
            )

            if field_process_func is not None:
                # Call processing function if it exists
                field_process_func(
                    parameters=parameters
                )

            # Call processing function to method section related to the current section
            section_method_parameters = section + '_' + self.field_labels['METHOD_PARAMETERS']

            if section in parameters and isinstance(parameters[section],
                                                    dict) and section_method_parameters in parameters:
                if self.field_labels['LABEL'] in parameters[section] or self.field_labels['RECIPE'] in parameters[section]:
                    field_process_parameters_func = getattr(
                        self,
                        '_process_{SECTION_NAME}_METHOD_PARAMETERS'.format(SECTION_NAME=section_name),
                        None
                    )

                    if field_process_parameters_func is not None:
                        field_process_parameters_func(parameters=parameters)

        # 2. Add parameter hash to methods
        self._add_hash_to_method_parameters(
            parameters=parameters
        )

        # 3. Parse recipes
        recipe_paths = parameters.get_leaf_path_list(target_field_endswith=self.field_labels['RECIPE'])
        for recipe_path in recipe_paths:
            parameters.set_path(
                path=recipe_path,
                new_value=VectorRecipeParser().parse(
                    recipe=parameters.get_path(path=recipe_path)
                )
            )

        # 4. Process methods
        for section in section_list:
            self._process_method_parameters(
                parameters=parameters,
                section=section
            )

        # 5. Inject dependencies
        for section in section_list:
            section_name = self.section_labels.flipped.map(section)
            if section_name:
                # Apply only named sections
                if self.get_path_translated(parameters=parameters, path=[section, 'PARAMETERS']):
                    for key, item in iteritems(self.get_path_translated(parameters=parameters, path=[section, 'PARAMETERS'])):

                        if self.method_dependencies.get_path([section_name, key]):
                            dependency_path = self._translated_path(
                                self.method_dependencies.get_path([section_name, key]).split('.')
                            )

                            if len(dependency_path) == 1:
                                section_method_parameters = section + '_' + self.field_labels['METHOD_PARAMETERS']

                                item[self.field_labels['DEPENDENCY_PARAMETERS']] = copy.deepcopy(
                                    parameters.get_path([section_method_parameters] + dependency_path[1:])
                                )

                                item[self.field_labels['DEPENDENCY_LABEL']] = dependency_path[-1]

                            elif len(dependency_path) == 2:
                                section_method_parameters = dependency_path[0] + '_' + self.field_labels[
                                    'METHOD_PARAMETERS']

                                item[self.field_labels['DEPENDENCY_PARAMETERS']] = copy.deepcopy(
                                    parameters.get_path([section_method_parameters] + dependency_path[1:])
                                )

                                item[self.field_labels['DEPENDENCY_LABEL']] = dependency_path[-1]

        # 6. Add hash
        self._add_hash_to_main_parameters(
            parameters=parameters
        )
        self._add_main_hash(
            parameters=parameters
        )

        # 7. Post process paths
        self._process_application_paths(
            parameters=parameters,
            create_paths=create_paths,
            create_parameter_hints=create_parameter_hints
        )

        return self

    def get_path_translated(self, path, parameters=None):
        """Get data with path, path can contain string constants which will be translated.

        Parameters
        ----------
        path : list of str
            Path parts

        parameters : dict
            Parameter dictionary. If none given self is used.
            Default value None

        Returns
        -------
        dict

        """

        if parameters is None:
            parameters = self

        return parameters.get_path(
            path=self._translated_path(path)
        )

    def set_path_translated(self, path, new_value, parameters=None):
        """Set data with path, path can contain string constants which will be translated.

        Parameters
        ----------
        path : list of str
            Path parts

        new_value : various
            Value to be set

        parameters : dict
            Parameter dictionary. If none given self is used.
            Default value None

        Returns
        -------
        None

        """

        if parameters is None:
            parameters = self

        return parameters.set_path(
            path=self._translated_path(path),
            new_value=new_value
        )

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

    def _process_method_parameters(self, parameters, section):
        """Process methods and recipes in the section

        Processing rules for fields:

        - "method" => search for parameters from [section]_method_parameters -section
        - "recipe" => parse recipe and search for parameters from [section]_method_parameters -section
        - "\*recipe" => parse recipe

        Parameters
        ----------
        parameters : dict
            Parameter dictionary

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

        if section in parameters and parameters[section] and isinstance(parameters[section], dict):
            # Get section name for method parameters
            section_method_parameters = self._method_parameter_section(
                section=section,
                parameters=parameters
            )

            # Inject method parameters
            if self.field_labels['LABEL'] in parameters[section]:
                if section_method_parameters in parameters and parameters[section][self.field_labels['LABEL']] in parameters[section_method_parameters]:
                    self.set_path_translated(
                        parameters=parameters,
                        path=[section, 'PARAMETERS'],
                        new_value=copy.deepcopy(
                            self.get_path_translated(
                                parameters=parameters,
                                path=[section_method_parameters, parameters[section][self.field_labels['LABEL']]]
                            )
                        )
                    )

                else:
                    message = '{name}: Invalid method for parameter field, {field}->method={method}'.format(
                        name=self.__class__.__name__,
                        field=section,
                        method=parameters[section][self.field_labels['LABEL']]
                    )

                    self.logger.exception(message)
                    raise ValueError(message)

            # Inject parameters based on recipes
            if self.field_labels['RECIPE'] in parameters[section]:
                # Remove current parameters
                self.set_path_translated(
                    parameters=parameters,
                    path=[section, 'PARAMETERS'],
                    new_value={}
                )

                for item in self.get_path_translated(parameters=parameters, path=[section, 'RECIPE']):

                    if self.field_labels['LABEL'] in item:
                        label = item[self.field_labels['LABEL']]

                    elif 'label' in item:
                        label = item['label']

                    method_parameters = self.get_path_translated(
                        parameters=parameters,
                        path=[section_method_parameters, label]
                    )

                    if method_parameters:
                        self.set_path_translated(
                            parameters=parameters,
                            path=[section, 'PARAMETERS', label],
                            new_value=method_parameters
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

    def _prepare_paths(self, parameters):
        """Prepare paths

        Parameters
        ----------
        parameters : dict
            Parameter dictionary

        """

        if self.section_labels['PATH'] in parameters:
            if platform.system() == 'Windows':
                # Translate separators if in Windows
                for path_key, path in iteritems(self.get_path_translated(parameters=parameters, path=['PATH'])):
                    if isinstance(path, str):
                        self.set_path_translated(
                            parameters=parameters,
                            path=['PATH', path_key],
                            new_value=Path(path).posix_to_nt()
                        )

                    elif isinstance(path, dict):
                        for path_key_sub, path_sub in iteritems(self.get_path_translated(parameters=parameters, path=['PATH', path_key])):
                            if isinstance(path_sub, str):
                                self.set_path_translated(
                                    parameters=parameters,
                                    path=['PATH', path_key, path_key_sub],
                                    new_value=Path(path_sub).posix_to_nt()
                                )

            # Translate paths to be absolute
            if self.get_path_translated(parameters=parameters, path=['PATH', 'APPLICATION_PATHS']):
                # Container has application paths

                if self.get_path_translated(parameters=parameters, path=['PATH', 'APPLICATION_PATHS', 'BASE']):
                    # Container has application base path
                    base_path = self.get_path_translated(parameters=parameters, path=['PATH', 'APPLICATION_PATHS', 'BASE'])

                    if not os.path.isabs(base_path):
                        base_path = os.path.join(self.app_base, base_path)
                        self.set_path_translated(
                            parameters=parameters,
                            path=['PATH', 'APPLICATION_PATHS', 'BASE'],
                            new_value=base_path
                        )

                else:
                    # No base path given, use main application base
                    base_path = self.app_base

                # Extend rest of the application paths
                for path_key, path in iteritems(self.get_path_translated(parameters=parameters, path=['PATH', 'APPLICATION_PATHS'])):
                    if path_key is not self.field_labels['BASE'] and not os.path.isabs(path):
                        path = os.path.join(base_path, path)
                        self.set_path_translated(
                            parameters=parameters,
                            path=['PATH', 'APPLICATION_PATHS', path_key],
                            new_value=path
                        )

            if self.get_path_translated(parameters=parameters, path=['PATH', 'EXTERNAL_PATHS']):
                # Container has external paths
                for path_key, path in iteritems(self.get_path_translated(parameters=parameters, path=['PATH', 'EXTERNAL_PATHS'])):
                    if not os.path.isabs(path):
                        path = os.path.join(self.app_base, path)
                        self.set_path_translated(
                            parameters=parameters,
                            path=['PATH', 'EXTERNAL_PATHS', path_key],
                            new_value=path
                        )

    def _process_application_paths(self, parameters, create_paths=True, create_parameter_hints=True):
        """Process application paths

        Parameters
        ----------
        parameters : dict
            Parameter dictionary

        create_paths : bool
            Create paths
            Default value True

        create_parameter_hints : bool
            Create parameters files to all data folders
            Default value True

        """

        # Make sure extended paths exists before saving parameters in them
        if create_paths:
            # Create paths
            paths = self.get_path_translated(
                parameters=parameters,
                path=['PATH']
            )

            if paths:
                for path_key, path in iteritems(paths):
                    if isinstance(path, str):
                        Path().create(path)

                    elif isinstance(path, dict):
                        for path_key_sub, path_sub in iteritems(self.get_path_translated(parameters=parameters, path=['PATH', path_key])):
                            if isinstance(path_sub, str):
                                Path().create(path_sub)

        # Check path_structure
        app_paths = self.get_path_translated(
            parameters=parameters,
            path=['PATH', 'APPLICATION_PATHS']
        )

        if app_paths:
            # Application paths are used
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
                    path = ApplicationPaths(
                        parameter_container=parameters
                    ).generate(
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
                        ApplicationPaths(
                            parameter_container=parameters
                        ).save_parameters_to_path(
                            path_base=path_base,
                            structure=structure,
                            parameter_filename=self.application_directory_parameter_filename
                        )

                    # Update path in the container
                    self.set_path_translated(
                        parameters=parameters,
                        path=['PATH', 'APPLICATION_PATHS', field],
                        new_value=path
                    )

    def _add_hash_to_main_parameters(self, parameters):
        """Add has to the main sections.

        Parameters
        ----------
        parameters : dict
            Parameter dictionary

        """

        for field, params in iteritems(parameters):
            if isinstance(params, dict):
                if field not in self.non_hashable_sections and parameters[field]:
                    parameters[field]['_hash'] = self.get_hash(
                        data=parameters[field]
                    )

    def _add_hash_to_method_parameters(self, parameters):
        """Add has to the method parameter sections.

        Parameters
        ----------
        parameters : dict
            Parameter dictionary

        """

        for field in parameters:
            if field.endswith('_' + self.field_labels['METHOD_PARAMETERS']):
                for key, params in iteritems(parameters[field]):
                    if params and isinstance(params, dict):
                        params['_hash'] = self.get_hash(
                            data=params
                        )

    def _add_main_hash(self, parameters):
        """Add main level hash.

        Parameters
        ----------
        parameters : dict
            Parameter dictionary

        """

        data = {}
        for field, params in iteritems(parameters):
            if isinstance(params, dict):
                if field not in self.non_hashable_sections and parameters[field]:
                    data[field] = self.get_hash(
                        data=parameters[field]
                    )

        parameters['_hash'] = self.get_hash(
            data=data
        )

    def _after_load(self, to_return=None):
        """Method triggered after parameters have been loaded."""
        self.processed = False

    def _clean_unused_parameters(self):
        """Remove unused parameters from the parameter dictionary."""
        for field in list(self.keys()):
            if field.endswith('_method_parameters'):
                del self[field]

    def _convert_main_level_to_containers(self, parameters):
        """Convert main level sections to DictContainers.

        Parameters
        ----------
        parameters : dict
            Parameter dictionary

        """

        for key, item in iteritems(parameters):
            if isinstance(item, dict) and self.field_labels['PARAMETERS'] in item:
                item[self.field_labels['PARAMETERS']] = DictContainer(item[self.field_labels['PARAMETERS']])

            if isinstance(item, dict):
                parameters[key] = DictContainer(item)

    def _method_parameter_section(self, section, parameters):
        """Get section name for method parameters.

        Parameters
        ----------
        section : str
            Section name

        parameters : dict
            Parameter dictionary

        Returns
        -------
        str

        """

        # Get LABEL for section
        section_label_map = OneToOneMappingContainer(self.section_labels)
        section_translation_label = section_label_map.flipped.map(section)

        # Test a few patterns to find method parameter section

        # Test pattern [LABEL + METHOD_PARAMETERS]
        method_parameter_section = section + '_' + self.field_labels['METHOD_PARAMETERS']

        if method_parameter_section not in parameters:
            if section_translation_label:
                # Test mapped [LABEL + '_METHOD_PARAMETERS']
                method_parameter_section = section_label_map.map(section_translation_label + '_METHOD_PARAMETERS')

                if method_parameter_section not in parameters:
                    # Test mapped [LABEL + '_PARAMETERS']
                    method_parameter_section = section_label_map.map(section_translation_label + '_PARAMETERS')

                    if method_parameter_section not in parameters:
                        # No fitting method parameter section found
                        method_parameter_section = None

            else:
                method_parameter_section = None

        return method_parameter_section

    def update_parameter_set(self, set_id):
        """Update active parameter set

        Parameters
        ----------
        set_id : str
            Set id used in set list

        Raises
        ------
        ValueError:
            No valid set id given

        Returns
        -------
        self

        """

        current_active_set = ListDictContainer(self[self.field_labels['SET-LIST']]).search(
            key=self.field_labels['SET-ID'],
            value=self[self.field_labels['ACTIVE-SET']]
        )

        new_active_set = ListDictContainer(self[self.field_labels['SET-LIST']]).search(
            key=self.field_labels['SET-ID'],
            value=set_id
        )

        if not new_active_set:
            message = '{name}: No valid set given [{set_name}]'.format(
                name=self.__class__.__name__,
                set_name=set_id
            )

            self.logger.exception(message)
            raise ValueError(message)

        # Clean up main level from old sections
        for section in current_active_set:
            if section in self:
                del self[section]

        # Update parameters
        self.merge(override=new_active_set)

        # Set new active set
        self[self.field_labels['ACTIVE-SET']] = set_id

        return self

    def set_ids(self):
        """Get set ids

        Returns
        -------
        list

        """

        if self.field_labels['SET-LIST'] in self:
            set_ids = []
            for set_id, set_defined_parameters in enumerate(self[self.field_labels['SET-LIST']]):
                if self.field_labels['SET-ID'] in set_defined_parameters:
                    set_ids.append(
                        set_defined_parameters[self.field_labels['SET-ID']]
                    )

            return sorted(set_ids)

        else:
            return None

    def set_id_exists(self, set_id):
        """Set id exists

        Parameters
        ----------
        set_id : str
            Parameter set id

        Returns
        -------
        bool

        """

        if set_id in self.set_ids():
            return True
        else:
            return False

    def active_set(self):
        """Get active set id


        Returns
        -------
        str

        """

        return self[self.field_labels['ACTIVE-SET']]

    def get_set(self, set_id):
        """Get parameter set

        Parameters
        ----------
        set_id : str
            Parameter set id

        Returns
        -------
        dict

        """

        if self.field_labels['SET-LIST'] in self and self.set_id_exists(set_id=set_id):
            for id, set_defined_parameters in enumerate(self[self.field_labels['SET-LIST']]):
                if self.field_labels['SET-ID'] in set_defined_parameters and set_defined_parameters[self.field_labels['SET-ID']] == set_id:
                    return set_defined_parameters

        else:
            return None


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
            'FEATURE_NORMALIZER_METHOD_PARAMETERS': 'feature_normalizer_method_parameters',
            'FEATURE_AGGREGATOR': 'feature_aggregator',
            'FEATURE_AGGREGATOR_METHOD_PARAMETERS': 'feature_aggregator_method_parameters',
            'FEATURE_SEQUENCER': 'feature_sequencer',
            'FEATURE_SEQUENCER_METHOD_PARAMETERS': 'feature_sequencer_method_parameters',
            'FEATURE_PROCESSING_CHAIN': 'feature_processing_chain',
            'FEATURE_PROCESSING_CHAIN_METHOD_PARAMETERS': 'feature_processing_chain_method_parameters',
            'DATA_PROCESSING_CHAIN': 'data_processing_chain',
            'DATA_PROCESSING_CHAIN_METHOD_PARAMETERS': 'data_processing_chain_method_parameters',
            'DATA_PROCESSING_CHAIN2': 'data_processing_chain2',
            'DATA_PROCESSING_CHAIN2_METHOD_PARAMETERS': 'data_processing_chain2_method_parameters',
            'META_PROCESSING_CHAIN': 'meta_processing_chain',
            'META_PROCESSING_CHAIN_METHOD_PARAMETERS': 'meta_processing_chain_method_parameters',
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
            'FEATURE_NORMALIZER_METHOD_PARAMETERS',
            'FEATURE_AGGREGATOR',
            'FEATURE_AGGREGATOR_METHOD_PARAMETERS',
            'FEATURE_SEQUENCER',
            'FEATURE_SEQUENCER_METHOD_PARAMETERS',
            'FEATURE_PROCESSING_CHAIN',
            'FEATURE_PROCESSING_CHAIN_METHOD_PARAMETERS',
            'DATA_PROCESSING_CHAIN',
            'DATA_PROCESSING_CHAIN_METHOD_PARAMETERS',
            'DATA_PROCESSING_CHAIN2',
            'DATA_PROCESSING_CHAIN2_METHOD_PARAMETERS',
            'META_PROCESSING_CHAIN',
            'META_PROCESSING_CHAIN_METHOD_PARAMETERS',
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
                'FEATURE_SEQUENCER',
                'LEARNER'
            ],
            'RECOGNIZER': [
                'FEATURE_EXTRACTOR',
                'FEATURE_STACKER',
                'FEATURE_NORMALIZER',
                'FEATURE_AGGREGATOR',
                'FEATURE_SEQUENCER',
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

    def _get_dependency_parameters_feature_extraction(self, parameters):
        # Get dependency parameters
        dependency_parameters = dict(self.get_path_translated(
            parameters=parameters,
            path=['FEATURE_EXTRACTOR']
        ))

        # Get section name for dependency method parameters
        dep_section_method_parameters = self._method_parameter_section(
            section=self.section_labels['FEATURE_EXTRACTOR'],
            parameters=parameters
        )

        # Inject parameters based on label
        if self.field_labels['LABEL'] in dependency_parameters:
            if dep_section_method_parameters in parameters and dependency_parameters[self.field_labels['LABEL']] in \
                    parameters[dep_section_method_parameters]:
                dependency_parameters[self.field_labels['PARAMETERS']] = copy.deepcopy(
                    dict(
                        self.get_path_translated(
                            parameters=parameters,
                            path=[dep_section_method_parameters, dependency_parameters[self.field_labels['LABEL']]]
                        )
                    )
                )

        # Inject parameters based on recipes
        if self.field_labels['RECIPE'] in dependency_parameters:
            # Remove current parameters
            dependency_parameters[self.field_labels['PARAMETERS']] = {}
            dependency_parameters[self.field_labels['RECIPE']] = VectorRecipeParser().parse(
                recipe=str(dependency_parameters[self.field_labels['RECIPE']])
            )

            for dep_item in dependency_parameters[self.field_labels['RECIPE']]:
                if self.field_labels['LABEL'] in dep_item:
                    label = dep_item[self.field_labels['LABEL']]

                elif 'label' in dep_item:
                    label = dep_item['label']

                label_parameters = dict(
                    self.get_path_translated(
                        parameters=parameters,
                        path=[dep_section_method_parameters, label]
                    )
                )

                if label_parameters:
                    dependency_parameters[self.field_labels['PARAMETERS']][label] = label_parameters

        return dependency_parameters

    def _process_LOGGING(self, parameters):
        """Process LOGGING section."""

        handlers = self.get_path_translated(
            parameters=parameters,
            path=['LOGGING', 'parameters', 'handlers']
        )

        if handlers:
            for handler_name, handler_data in iteritems(handlers):
                if 'filename' in handler_data:
                    if parameters.get_path(path=self.section_labels['PATH'] + '.'+self.section_labels['EXTERNAL_PATHS'] + '.logs'):
                        handler_data['filename'] = os.path.join(
                            self.get_path_translated(
                                parameters=parameters,
                                path=['PATH', 'EXTERNAL_PATHS', 'logs']
                            ),
                            handler_data['filename']
                        )

                    elif parameters.get_path(path=self.section_labels['PATH'] + '.'+self.section_labels['APPLICATION_PATHS'] + '.logs'):
                        handler_data['filename'] = os.path.join(
                            self.get_path_translated(
                                parameters=parameters,
                                path=['PATH', 'APPLICATION_PATHS', 'logs']
                            ),
                            handler_data['filename']
                        )

    def _process_FEATURE_EXTRACTOR(self, parameters):
        """Process FEATURE_EXTRACTION section."""

        if not self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'RECIPE']) and self.get_path_translated(parameters=parameters, path=['FEATURE_STACKER', 'STACKING_RECIPE']):
            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_EXTRACTOR', 'RECIPE'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['FEATURE_STACKER', 'STACKING_RECIPE']
                )
            )

        # Calculate window length in samples
        if self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'win_length_seconds']) and self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'fs']):
            win_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['FEATURE_EXTRACTOR', 'win_length_seconds']
            )

            fs = self.get_path_translated(
                parameters=parameters,
                path=['FEATURE_EXTRACTOR', 'fs']
            )

            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_EXTRACTOR', 'win_length_samples'],
                new_value=int(win_length_seconds * fs)
            )

        # Calculate hop length in samples
        if self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'hop_length_seconds']) and self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'fs']):
            hop_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['FEATURE_EXTRACTOR', 'hop_length_seconds']
            )

            fs = self.get_path_translated(
                parameters=parameters,
                path=['FEATURE_EXTRACTOR', 'fs']
            )

            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_EXTRACTOR', 'hop_length_samples'],
                new_value=int(hop_length_seconds * fs)
            )

    def _process_FEATURE_NORMALIZER(self, parameters):
        """Process FEATURE_NORMALIZER section."""

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_NORMALIZER', 'scene_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'scene_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_NORMALIZER', 'active_scenes'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_scenes']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_NORMALIZER', 'event_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'event_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_events']):
            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_NORMALIZER', 'active_events'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_events']
                )
            )

    def _process_FEATURE_EXTRACTOR_METHOD_PARAMETERS(self, parameters):
        """Process FEATURE_EXTRACTOR_METHOD_PARAMETERS section."""

        # Get section name for method parameters
        method_parameter_field = self._method_parameter_section(
            section=self.section_labels['FEATURE_EXTRACTOR'],
            parameters=parameters
        )
        if method_parameter_field in parameters:
            # Change None feature parameter sections into empty dicts
            for label in list(parameters[method_parameter_field].keys()):
                if parameters[method_parameter_field][label] is None:
                    parameters[method_parameter_field][label] = {}

            for label, data in iteritems(parameters[method_parameter_field]):
                # Add label
                data[self.field_labels['LABEL']] = label

                # Copy general parameters
                if self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'fs']):
                    data['fs'] = self.get_path_translated(
                        parameters=parameters,
                        path=['FEATURE_EXTRACTOR', 'fs']
                    )

                if self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'win_length_seconds']):
                    data['win_length_seconds'] = self.get_path_translated(
                        parameters=parameters,
                        path=['FEATURE_EXTRACTOR', 'win_length_seconds']
                    )

                if self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'win_length_samples']):
                    data['win_length_samples'] = self.get_path_translated(
                        parameters=parameters,
                        path=['FEATURE_EXTRACTOR', 'win_length_samples']
                    )

                if self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'hop_length_seconds']):
                    data['hop_length_seconds'] = self.get_path_translated(
                        parameters=parameters,
                        path=['FEATURE_EXTRACTOR', 'hop_length_seconds']
                    )

                if self.get_path_translated(parameters=parameters, path=['FEATURE_EXTRACTOR', 'hop_length_samples']):
                    data['hop_length_samples'] = self.get_path_translated(
                        parameters=parameters,
                        path=['FEATURE_EXTRACTOR', 'hop_length_samples']
                    )

    def _process_FEATURE_AGGREGATOR(self, parameters):
        """Process FEATURE_AGGREGATOR section."""
        win_length_seconds_aggregator = self.get_path_translated(
            parameters=parameters,
            path=['FEATURE_AGGREGATOR', 'win_length_seconds']
        )

        win_length_seconds_feature_extraction = self.get_path_translated(
            parameters=parameters,
            path=['FEATURE_EXTRACTOR', 'win_length_seconds']
        )

        if win_length_seconds_aggregator and win_length_seconds_feature_extraction:

            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_AGGREGATOR', 'win_length_frames'],
                new_value=int(numpy.ceil(win_length_seconds_aggregator / float(win_length_seconds_feature_extraction)))
            )

        hop_length_seconds_aggregator = self.get_path_translated(
            parameters=parameters,
            path=['FEATURE_AGGREGATOR', 'hop_length_seconds']
        )

        win_length_seconds_feature_extraction = self.get_path_translated(
            parameters=parameters,
            path=['FEATURE_EXTRACTOR', 'win_length_seconds']
        )

        if hop_length_seconds_aggregator and win_length_seconds_feature_extraction:
            self.set_path_translated(
                parameters=parameters,
                path=['FEATURE_AGGREGATOR', 'hop_length_frames'],
                new_value=int(numpy.ceil(hop_length_seconds_aggregator / float(win_length_seconds_feature_extraction)))
            )

    def _process_FEATURE_PROCESSING_CHAIN_METHOD_PARAMETERS(self, parameters):
        """Process FEATURE_PROCESSING_CHAIN_METHOD_PARAMETERS section."""

        # Get section name for method parameters
        section_method_parameters = self._method_parameter_section(
            section=self.section_labels['FEATURE_PROCESSING_CHAIN'],
            parameters=parameters
        )

        if section_method_parameters in parameters:
            # Change None feature parameter sections into empty dicts
            for label in list(parameters[section_method_parameters].keys()):
                if parameters[section_method_parameters][label] is None:
                    parameters[section_method_parameters][label] = {}

            for label, data in iteritems(parameters[section_method_parameters]):
                # Add label
                data[self.field_labels['LABEL']] = label

                if self.field_labels['CHAIN'] in data:
                    # Collect enabled items from the processing chain.
                    enabled_items = []
                    for item_id, item in enumerate(data[self.field_labels['CHAIN']]):
                        if 'RepositoryFeatureExtractorProcessor' in item['processor_name']:
                            # Get dependency parameters
                            item['init_parameters'] = {
                                'parameters': self._get_dependency_parameters_feature_extraction(
                                    parameters=parameters
                                )['parameters']
                            }

                        elif 'FeatureExtractorProcessor' in item['processor_name']:
                            item['init_parameters'] = self._get_dependency_parameters_feature_extraction(
                                parameters=parameters
                            )['parameters']

                        elif 'FeatureReadingProcessor' in item['processor_name']:
                            # Get dependency parameters
                            dependency_parameters = self._get_dependency_parameters_feature_extraction(
                                parameters=parameters
                            )

                            # Inject feature extraction parameters to get correct hash value
                            item[self.field_labels['DEPENDENCY_PARAMETERS']] = dependency_parameters

                        init_parameters = item.get('init_parameters', {})
                        if self.field_labels['ENABLE'] in init_parameters and init_parameters[self.field_labels['ENABLE']]:
                            enabled_items.append(item)

                        elif self.field_labels['ENABLE'] not in init_parameters:
                            enabled_items.append(item)

                    data[self.field_labels['CHAIN']] = enabled_items

    def _process_DATA_PROCESSING_CHAIN_METHOD_PARAMETERS(self, parameters, section_method_parameters=None):
        """Process DATA_PROCESSING_CHAIN_METHOD_PARAMETERS section."""

        # Get section name for method parameters
        if section_method_parameters is None:
            section_method_parameters = self._method_parameter_section(
                section=self.section_labels['DATA_PROCESSING_CHAIN'],
                parameters=parameters
            )

        if section_method_parameters in parameters:
            # Change None feature parameter sections into empty dicts
            for label in list(parameters[section_method_parameters].keys()):
                if parameters[section_method_parameters][label] is None:
                    parameters[section_method_parameters][label] = {}

            for label, data in iteritems(parameters[section_method_parameters]):
                # Add label
                data[self.field_labels['LABEL']] = label

                if self.field_labels['CHAIN'] in data:
                    # Collect enabled items from the processing chain.
                    enabled_items = []
                    for item_id, item in enumerate(data[self.field_labels['CHAIN']]):
                        if 'RepositoryFeatureExtractorProcessor' in item['processor_name']:
                            # Get dependency parameters
                            item['init_parameters'] = {
                                'parameters': self._get_dependency_parameters_feature_extraction(
                                    parameters=parameters
                                )['parameters']
                            }

                        elif 'FeatureExtractorProcessor' in item['processor_name']:
                            item['init_parameters'] = self._get_dependency_parameters_feature_extraction(
                                parameters=parameters
                            )['parameters']

                        elif 'FeatureReadingProcessor' in item['processor_name']:
                            # Get dependency parameters
                            dependency_parameters = dict(self.get_path_translated(
                                parameters=parameters,
                                path=['FEATURE_EXTRACTOR']
                            ))

                            # Get section name for dependency method parameters
                            dep_section_method_parameters = self._method_parameter_section(
                                section=self.section_labels['FEATURE_EXTRACTOR'],
                                parameters=parameters
                            )
                            # Inject parameters based on label
                            if self.field_labels['LABEL'] in dependency_parameters:
                                if dep_section_method_parameters in parameters and dependency_parameters[self.field_labels['LABEL']] in parameters[dep_section_method_parameters]:
                                    dependency_parameters[self.field_labels['PARAMETERS']] = copy.deepcopy(
                                        dict(
                                            self.get_path_translated(
                                                parameters=parameters,
                                                path=[dep_section_method_parameters, dependency_parameters[self.field_labels['LABEL']]]
                                            )
                                        )
                                    )

                            # Inject parameters based on recipes
                            if self.field_labels['RECIPE'] in dependency_parameters:
                                # Remove current parameters
                                dependency_parameters[self.field_labels['PARAMETERS']] = {}
                                dependency_parameters[self.field_labels['RECIPE']] = VectorRecipeParser().parse(
                                    recipe=str(dependency_parameters[self.field_labels['RECIPE']])
                                )

                                for dep_item in dependency_parameters[self.field_labels['RECIPE']]:
                                    if self.field_labels['LABEL'] in dep_item:
                                        label = dep_item[self.field_labels['LABEL']]

                                    elif 'label' in dep_item:
                                        label = dep_item['label']

                                    label_parameters = dict(
                                        self.get_path_translated(
                                            parameters=parameters,
                                            path=[dep_section_method_parameters, label]
                                        )
                                    )

                                    if label_parameters:
                                        dependency_parameters[self.field_labels['PARAMETERS']][label] = label_parameters

                            # Inject feature extraction parameters to get correct hash value
                            item[self.field_labels['DEPENDENCY_PARAMETERS']] = dependency_parameters

                        elif 'StackingProcessor' in item['processor_name']:
                            recipe = self.get_path_translated(
                                parameters=parameters,
                                path=['FEATURE_STACKER', 'STACKING_RECIPE']
                            )
                            if recipe:
                                if 'init_parameters' not in item:
                                    item['init_parameters'] = {}

                                item['init_parameters']['recipe'] = recipe

                        init_parameters = item.get('init_parameters', {})
                        if self.field_labels['ENABLE'] in init_parameters and init_parameters[self.field_labels['ENABLE']]:
                            enabled_items.append(item)

                        elif self.field_labels['ENABLE'] not in init_parameters:
                            enabled_items.append(item)

                    data[self.field_labels['CHAIN']] = enabled_items

    def _process_DATA_PROCESSING_CHAIN2_METHOD_PARAMETERS(self, parameters):
        """Process DATA_PROCESSING_CHAIN2_METHOD_PARAMETERS section."""

        self._process_DATA_PROCESSING_CHAIN_METHOD_PARAMETERS(
            parameters=parameters,
            section_method_parameters=self._method_parameter_section(
                section=self.section_labels['DATA_PROCESSING_CHAIN2'],
                parameters=parameters
            )
        )

    def _process_META_PROCESSING_CHAIN_METHOD_PARAMETERS(self, parameters, section_method_parameters=None):
        """Process META__PROCESSING_CHAIN_METHOD_PARAMETERS section."""

        # Get section name for method parameters
        if section_method_parameters is None:
            section_method_parameters = self._method_parameter_section(
                section=self.section_labels['META_PROCESSING_CHAIN'],
                parameters=parameters
            )

        if section_method_parameters in parameters:
            # Change None feature parameter sections into empty dicts
            for label in list(parameters[section_method_parameters].keys()):
                if parameters[section_method_parameters][label] is None:
                    parameters[section_method_parameters][label] = {}

            for label, data in iteritems(parameters[section_method_parameters]):
                # Add label
                data[self.field_labels['LABEL']] = label

                if self.field_labels['CHAIN'] in data:
                    # Collect enabled items from the processing chain.
                    enabled_items = []
                    for item_id, item in enumerate(data[self.field_labels['CHAIN']]):

                        init_parameters = item.get('init_parameters', {})
                        if self.field_labels['ENABLE'] in init_parameters and init_parameters[self.field_labels['ENABLE']]:
                            enabled_items.append(item)

                        elif self.field_labels['ENABLE'] not in init_parameters:
                            enabled_items.append(item)

                    data[self.field_labels['CHAIN']] = enabled_items

    def _process_LEARNER(self, parameters):
        """Process LEARNER section."""

        # Process window length and hop length
        win_length_seconds = self.get_path_translated(
            parameters=parameters,
            path=['FEATURE_EXTRACTOR', 'win_length_seconds']
        )
        hop_length_seconds = self.get_path_translated(
            parameters=parameters,
            path=['FEATURE_EXTRACTOR', 'hop_length_seconds']
        )

        if self.get_path_translated(parameters=parameters, path=['FEATURE_AGGREGATOR', 'enable']):
            win_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['FEATURE_AGGREGATOR', 'win_length_seconds']
            )

            hop_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['FEATURE_AGGREGATOR', 'hop_length_seconds']
            )

        if win_length_seconds:
            self.set_path_translated(
                parameters=parameters,
                path=['LEARNER', 'win_length_seconds'],
                new_value=float(win_length_seconds)
            )

        if hop_length_seconds:
            self.set_path_translated(
                parameters=parameters,
                path=['LEARNER', 'hop_length_seconds'],
                new_value=float(hop_length_seconds)
            )

        # Process specifiers
        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['LEARNER', 'scene_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'scene_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                parameters=parameters,
                path=['LEARNER', 'active_scenes'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_scenes']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['LEARNER', 'event_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'event_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_events']):
            self.set_path_translated(
                parameters=parameters,
                path=['LEARNER', 'active_events'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_events']
                )
            )

    def _process_LEARNER_METHOD_PARAMETERS(self, parameters):
        """Process LEARNER_METHOD_PARAMETERS section."""

        method_parameter_field = self.section_labels['LEARNER'] + '_' + self.field_labels['METHOD_PARAMETERS']

        if method_parameter_field in parameters:
            for method, data in iteritems(parameters[method_parameter_field]):
                data = DictContainer(data)
                if data.get_path('training.epoch_processing.enable') and not data.get_path('training.epoch_processing.recognizer'):
                    data['training']['epoch_processing']['recognizer'] = self.get_path_translated(
                        parameters=parameters,
                        path=['RECOGNIZER']
                    )

                if data.get_path('model.sets'):
                    data['model']['set_parameters'] = []
                    for set_id in data.get_path('model.sets'):
                        data['model']['set_parameters'].append(
                          self.get_set(set_id=set_id)
                        )

    def _process_RECOGNIZER(self, parameters):
        """Process RECOGNIZER section."""

        # Process specifiers
        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'scene_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'scene_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'active_scenes'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_scenes']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'event_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'event_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_events']):
            self.set_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'active_events'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_events']
                )
            )

        # Inject frame accumulation parameters
        if (self.get_path_translated(parameters=parameters, path=['RECOGNIZER', 'frame_accumulation', 'enable']) and
                self.get_path_translated(parameters=parameters, path=['RECOGNIZER', 'frame_accumulation', 'window_length_seconds'])):

            window_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'frame_accumulation', 'window_length_seconds']
            )

            hop_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['LEARNER', 'hop_length_seconds']
            )

            self.set_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'frame_accumulation', 'window_length_frames'],
                new_value=int(window_length_seconds / float(hop_length_seconds))
            )

        # Inject event activity processing parameters
        if self.get_path_translated(parameters=parameters, path=['RECOGNIZER', 'event_activity_processing', 'enable']) and self.get_path_translated(parameters=parameters, path=['RECOGNIZER', 'event_activity_processing', 'window_length_seconds']):
            window_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'event_activity_processing', 'window_length_seconds']
            )

            hop_length_seconds = self.get_path_translated(
                parameters=parameters,
                path=['LEARNER', 'hop_length_seconds']
            )

            self.set_path_translated(
                parameters=parameters,
                path=['RECOGNIZER', 'event_activity_processing', 'window_length_frames'],
                new_value=int(window_length_seconds / float(hop_length_seconds))
            )

    def _process_EVALUATOR(self, parameters):
        """Process EVALUATOR section."""

        # Process specifiers
        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'scene_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['EVALUATOR', 'scene_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'scene_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_scenes']):
            self.set_path_translated(
                parameters=parameters,
                path=['EVALUATOR', 'active_scenes'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_scenes']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'event_handling']):
            self.set_path_translated(
                parameters=parameters,
                path=['EVALUATOR', 'event_handling'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'event_handling']
                )
            )

        if self.get_path_translated(parameters=parameters, path=['GENERAL', 'active_events']):
            self.set_path_translated(
                parameters=parameters,
                path=['EVALUATOR', 'active_events'],
                new_value=self.get_path_translated(
                    parameters=parameters,
                    path=['GENERAL', 'active_events']
                )
            )


class ParameterListContainer(ListDictContainer):
    """Parameter list container, inherited from ListDictContainer."""
    valid_formats = ['yaml']  #: Valid file formats

