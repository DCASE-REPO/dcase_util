# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
import importlib
import logging

from dcase_util.containers import DictContainer
from dcase_util.ui import FancyStringifier, FancyHTMLStringifier
from dcase_util.utils import SimpleMathStringEvaluator, setup_logging, is_jupyter


def create_sequential_model(model_parameter_list, input_shape=None, output_shape=None, constants=None, return_functional=False):
    """Create sequential Keras model

    Example parameters::

        model_parameter_list = [
            {
                'class_name': 'Dense',
                'config': {
                    'units': 'CONSTANT_B',
                    'kernel_initializer': 'uniform',
                    'activation': 'relu'
                }
            },
            {
                'class_name': 'Dropout',
                'config': {
                    'rate': 0.2
                }
            },
            {
                'class_name': 'Dense',
                'config': {
                    'units': 'CONSTANT_A' * 2,
                    'kernel_initializer': 'uniform',
                    'activation': 'relu'
                }
            },
            {
                'class_name': 'Dropout',
                'config': {
                    'rate': 0.2
                }
            },
            {
                'class_name': 'Dense',
                'config': {
                    'units': 'CLASS_COUNT',
                    'kernel_initializer': 'uniform',
                    'activation': 'softmax'
                }
            }
        ]
        constants = {
            'CONSTANT_A': 50,
            'CONSTANT_B': 100
        }

    Parameters
    ----------
    model_parameter_list : dict or DictContainer
        Model parameters

    input_shape : int
        Size of the input layer
        Default value None

    output_shape : int
        Size of the output layer
        Default value None

    constants : dict or DictContainer
        Constants used in the model_parameter definitions.
        Default value None

    return_functional : bool
        Convert sequential model into function model.
        Default value False

    Returns
    -------
    Keras model

    """

    from keras.models import Sequential
    keras_model = Sequential()

    tuple_fields = [
        'input_shape',
        'kernel_size',
        'pool_size',
        'dims',
        'target_shape',
        'strides'
    ]

    # Get constants for model
    if constants is None:
        constants = {}

    if 'INPUT_SHAPE' not in constants and input_shape is not None:
        constants['INPUT_SHAPE'] = input_shape

    if 'OUTPUT_SHAPE' not in constants and output_shape is not None:
        constants['OUTPUT_SHAPE'] = output_shape

    if 'CLASS_COUNT' not in constants:
        constants['CLASS_COUNT'] = output_shape

    if 'FEATURE_VECTOR_LENGTH' not in constants:
        constants['FEATURE_VECTOR_LENGTH'] = input_shape

    def logger():
        logger_instance = logging.getLogger(__name__)
        if not logger_instance.handlers:
            setup_logging()
        return logger_instance

    def process_field(value, constants_dict):
        math_eval = SimpleMathStringEvaluator()

        if isinstance(value, str):
            sub_fields = value.split()
            if len(sub_fields) > 1:
                # Inject constants to math formula
                for subfield_id, subfield in enumerate(sub_fields):
                    if subfield in constants_dict:
                        sub_fields[subfield_id] = str(constants_dict[subfield])
                value = ''.join(sub_fields)

            else:
                # Inject constants
                if value in constants_dict:
                    value = str(constants_dict[value])

            return math_eval.eval(value)

        elif isinstance(value, list):
            processed_value_list = []
            for item_id, item in enumerate(value):
                processed_value_list.append(
                    process_field(
                        value=item,
                        constants_dict=constants_dict
                    )
                )

            return processed_value_list

        else:
            return value

    # Inject constant into constants with equations
    for field in list(constants.keys()):
        constants[field] = process_field(
            value=constants[field],
            constants_dict=constants
        )

    # Setup layers
    for layer_id, layer_setup in enumerate(model_parameter_list):
        # Get layer parameters
        layer_setup = DictContainer(layer_setup)
        if 'config' not in layer_setup:
            layer_setup['config'] = {}

        # Get layer class
        try:
            layer_class = getattr(
                importlib.import_module('keras.layers'),
                layer_setup['class_name']
            )

        except AttributeError:
            message = 'Invalid Keras layer type [{type}].'.format(
                type=layer_setup['class_name']
            )
            logger().exception(message)
            raise AttributeError(message)

        # Inject constants
        for config_field in list(layer_setup['config'].keys()):
            layer_setup['config'][config_field] = process_field(
                value=layer_setup['config'][config_field],
                constants_dict=constants
            )

        # Convert lists into tuples
        for field in tuple_fields:
            if field in layer_setup['config'] and isinstance(layer_setup['config'][field], list):
                layer_setup['config'][field] = tuple(layer_setup['config'][field])

        # Inject input shape for Input layer if not given
        if layer_id == 0 and layer_setup.get_path('config.input_shape') is None and input_shape is not None:
            # Set input layer dimension for the first layer if not set
            layer_setup['config']['input_shape'] = (input_shape,)

        if 'wrapper' in layer_setup:
            # Get layer wrapper class
            try:
                wrapper_class = getattr(
                    importlib.import_module("keras.layers"),
                    layer_setup['wrapper']
                )

            except AttributeError:
                message = 'Invalid Keras layer wrapper type [{type}].'.format(
                    type=layer_setup['wrapper']
                )
                logger().exception(message)
                raise AttributeError(message)

            wrapper_parameters = layer_setup.get('config_wrapper', {})

            if layer_setup.get('config'):
                keras_model.add(
                    wrapper_class(layer_class(**dict(layer_setup.get('config'))), **dict(wrapper_parameters)))
            else:
                keras_model.add(wrapper_class(layer_class(), **dict(wrapper_parameters)))

        else:
            if layer_setup.get('config'):
                keras_model.add(layer_class(**dict(layer_setup.get('config'))))
            else:
                keras_model.add(layer_class())

    if return_functional:
        from keras.layers import Input
        from keras.models import Model
        input_layer = Input(batch_shape=keras_model.layers[0].input_shape)
        prev_layer = input_layer
        for layer in keras_model.layers:
            prev_layer = layer(prev_layer)

        keras_model = Model(
            inputs=[input_layer],
            outputs=[prev_layer]
        )

    return keras_model


def model_summary_string(keras_model, mode='keras', show_parameters=True, display=False):
    """Model summary in a formatted string, similar to Keras model summary function.

    Parameters
    ----------
    keras_model : keras model
        Keras model

    mode : str
        Summary mode ['extended', 'keras']. In case 'keras', standard Keras summary is returned.
        Default value keras

    show_parameters : bool
        Show model parameter count and input / output shapes
        Default value True

    display : bool
        Display summary immediately, otherwise return string
        Default value False

    Returns
    -------
    str
        Model summary

    """

    if is_jupyter():
        ui = FancyHTMLStringifier()
        html_mode = True
    else:
        ui = FancyStringifier()
        html_mode = False

    output = ''
    output += ui.line('Model summary') + '\n'

    if mode == 'extended' or mode == 'extended_wide':
        layer_name_map = {
            'BatchNormalization': 'BatchNorm',
        }

        layer_type_html_tags = {
            'InputLayer': '<span class="label label-default">{0:s}</span>',
            'Dense': '<span class="label label-primary">{0:s}</span>',
            'TimeDistributed': '<span class="label label-primary">{0:s}</span>',

            'BatchNorm': '<span class="label label-default">{0:s}</span>',
            'Activation': '<span class="label label-default">{0:s}</span>',
            'Dropout': '<span class="label label-default">{0:s}</span>',

            'Flatten': '<span class="label label-success">{0:s}</span>',
            'Reshape': '<span class="label label-success">{0:s}</span>',
            'Permute': '<span class="label label-success">{0:s}</span>',

            'Conv1D': '<span class="label label-warning">{0:s}</span>',
            'Conv2D': '<span class="label label-warning">{0:s}</span>',

            'MaxPooling1D': '<span class="label label-success">{0:s}</span>',
            'MaxPooling2D': '<span class="label label-success">{0:s}</span>',
            'MaxPooling3D': '<span class="label label-success">{0:s}</span>',
            'AveragePooling1D': '<span class="label label-success">{0:s}</span>',
            'AveragePooling2D': '<span class="label label-success">{0:s}</span>',
            'AveragePooling3D': '<span class="label label-success">{0:s}</span>',
            'GlobalMaxPooling1D': '<span class="label label-success">{0:s}</span>',
            'GlobalMaxPooling2D': '<span class="label label-success">{0:s}</span>',
            'GlobalMaxPooling3D': '<span class="label label-success">{0:s}</span>',
            'GlobalAveragePooling1D': '<span class="label label-success">{0:s}</span>',
            'GlobalAveragePooling2D': '<span class="label label-success">{0:s}</span>',
            'GlobalAveragePooling3D': '<span class="label label-success">{0:s}</span>',

            'RNN': '<span class="label label-danger">{0:s}</span>',
            'SimpleRNN': '<span class="label label-danger">{0:s}</span>',
            'GRU': '<span class="label label-danger">{0:s}</span>',
            'CuDNNGRU': '<span class="label label-danger">{0:s}</span>',
            'LSTM': '<span class="label label-danger">{0:s}</span>',
            'CuDNNLSTM': '<span class="label label-danger">{0:s}</span>',
            'Bidirectional': '<span class="label label-danger">{0:s}</span>'
        }

        import keras
        from distutils.version import LooseVersion
        import keras.backend as keras_backend

        table_data = {
            'layer_type': [],
            'output': [],
            'parameter_count': [],
            'name': [],
            'connected_to': [],
            'activation': [],
            'initialization': []
        }

        row_separators = []
        prev_name = None
        for layer_id, layer in enumerate(keras_model.layers):
            connections = []
            if LooseVersion(keras.__version__) >= LooseVersion('2.1.3'):
                for node_index, node in enumerate(layer._inbound_nodes):
                    for i in range(len(node.inbound_layers)):
                        inbound_layer = node.inbound_layers[i].name
                        inbound_node_index = node.node_indices[i]
                        inbound_tensor_index = node.tensor_indices[i]
                        connections.append(
                            inbound_layer + '[' + str(inbound_node_index) + '][' + str(inbound_tensor_index) + ']'
                        )

            else:
                for node_index, node in enumerate(layer.inbound_nodes):
                    for i in range(len(node.inbound_layers)):
                        inbound_layer = node.inbound_layers[i].name
                        inbound_node_index = node.node_indices[i]
                        inbound_tensor_index = node.tensor_indices[i]
                        connections.append(
                            inbound_layer + '[' + str(inbound_node_index) + '][' + str(inbound_tensor_index) + ']'
                        )

            config = DictContainer(layer.get_config())
            layer_name = layer.__class__.__name__
            if layer_name in layer_name_map:
                layer_name = layer_name_map[layer_name]

            if html_mode and layer_name in layer_type_html_tags:
                layer_name = layer_type_html_tags[layer_name].format(layer_name)

            if config.get_path('kernel_initializer.class_name') == 'VarianceScaling':
                init = str(config.get_path('kernel_initializer.config.distribution', '---'))

            elif config.get_path('kernel_initializer.class_name') == 'RandomUniform':
                init = 'uniform'

            else:
                init = '-'

            name_parts = layer.name.split('_')
            if prev_name != name_parts[0]:
                row_separators.append(layer_id)
                prev_name = name_parts[0]

            table_data['layer_type'].append(layer_name)
            table_data['output'].append(str(layer.output_shape))
            table_data['parameter_count'].append(str(layer.count_params()))
            table_data['name'].append(layer.name)
            table_data['connected_to'].append(str(connections[0]) if len(connections) > 0 else '-')
            table_data['activation'].append(str(config.get('activation', '-')))
            table_data['initialization'].append(init)

        trainable_count = int(
            numpy.sum([keras_backend.count_params(p) for p in set(keras_model.trainable_weights)])
        )

        non_trainable_count = int(
            numpy.sum([keras_backend.count_params(p) for p in set(keras_model.non_trainable_weights)])
        )

        # Show row separators only if they are useful
        if len(row_separators) == len(keras_model.layers):
            row_separators = None
        if mode == 'extended':
            output += ui.table(
                cell_data=[table_data['name'], table_data['layer_type'], table_data['output'], table_data['parameter_count']],
                column_headers=['Layer name', 'Layer type', 'Output shape', 'Parameters'],
                column_types=['str30', 'str20', 'str25', 'str20'],
                column_separators=[1, 2],
                row_separators=row_separators,
                indent=4
            )

        elif mode == 'extended_wide':
            output += ui.table(
                cell_data=[table_data['name'], table_data['layer_type'], table_data['output'], table_data['parameter_count'],
                           table_data['activation'], table_data['initialization']],
                column_headers=['Layer name', 'Layer type', 'Output shape', 'Parameters', 'Act.', 'Init.'],
                column_types=['str30', 'str20', 'str25', 'str20', 'str15', 'str15'],
                column_separators=[1, 2, 3],
                row_separators=row_separators,
                indent=4
            )

        if show_parameters:
            output += ui.line('') + '\n'
            output += ui.line('Parameters', indent=4) + '\n'
            output += ui.data(indent=6, field='Total', value=trainable_count + non_trainable_count) + '\n'
            output += ui.data(indent=6, field='Trainable', value=trainable_count) + '\n'
            output += ui.data(indent=6, field='Non-Trainable', value=non_trainable_count) + '\n'

    else:
        output_buffer = []
        keras_model.summary(print_fn=output_buffer.append)
        for line in output_buffer:
            if is_jupyter():
                output += ui.line('<code>'+line+'</code>', indent=4) + '\n'
            else:
                output += ui.line(line, indent=4) + '\n'

    model_config = keras_model.get_config()

    if show_parameters:
        output += ui.line('') + '\n'
        output += ui.line('Input', indent=4) + '\n'
        output += ui.data(indent=6, field='Shape', value=keras_model.input_shape) + '\n'

        output += ui.line('Output', indent=4) + '\n'
        output += ui.data(indent=6, field='Shape', value=keras_model.output_shape) + '\n'

        if isinstance(model_config, dict) and 'layers' in model_config:
            output += ui.data(
                indent=6,
                field='Activation',
                value=model_config['layers'][-1]['config'].get('activation')
            ) + '\n'

        elif isinstance(model_config, list):
            output += ui.data(
                indent=6,
                field='Activation',
                value=model_config[-1].get('config', {}).get('activation')
            ) + '\n'

    if display:
        if is_jupyter():
            from IPython.core.display import display, HTML
            display(HTML(output))

        else:
            print(output)

    else:
        return output


