# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
import importlib
import logging

from dcase_util.containers import DictContainer
from dcase_util.ui import FancyStringifier
from dcase_util.utils import SimpleMathStringEvaluator, setup_logging


def create_sequential_model(model_parameter_list, input_shape=None, output_shape=None, constants=None):
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

    output_shape : int
        Size of the output layer

    constants : dict or DictContainer
        Constants used in the model_parameter definitions.

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
        'target_shape'
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
            # String field
            if value in constants_dict:
                return constants_dict[value]

            elif len(value.split()) > 1:
                sub_fields = value.split()
                for subfield_id, subfield in enumerate(sub_fields):
                    if subfield in constants_dict:
                        sub_fields[subfield_id] = str(constants_dict[subfield])

                return math_eval.eval(''.join(sub_fields))

            else:
                return value

        elif isinstance(value, list):
            processed_value_list = []
            for item_id, item in enumerate(value):
                processed_value_list.append(process_field(value=item, constants_dict=constants_dict))

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
                importlib.import_module("keras.layers"),
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
            if field in layer_setup['config']:
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

    return keras_model


def model_summary_string(keras_model):
    """Model summary in a string, similar to Keras model summary function.

    Parameters
    ----------
    keras_model : keras model
        Keras model

    Returns
    -------
    str
        Model summary

    """

    ui = FancyStringifier()
    layer_name_map = {
        'BatchNormalization': 'BatchNorm',
    }
    import keras.backend as keras_backend

    output = ''
    output += ui.line('Model summary') + '\n'
    output += ui.row(
        'Layer type', 'Output', 'Param', 'Name', 'Connected to', 'Activ.', 'Init',
        widths=[15, 20, 10, 20, 25, 10, 10],
        indent=4
    ) + '\n'
    output += ui.row('-', '-', '-', '-', '-', '-', '-') + '\n'

    for layer in keras_model.layers:
        connections = []
        for node_index, node in enumerate(layer.inbound_nodes):
            for i in range(len(node.inbound_layers)):
                inbound_layer = node.inbound_layers[i].name
                inbound_node_index = node.node_indices[i]
                inbound_tensor_index = node.tensor_indices[i]
                connections.append(inbound_layer + '[' + str(inbound_node_index) +
                                   '][' + str(inbound_tensor_index) + ']')

        config = DictContainer(layer.get_config())
        layer_name = layer.__class__.__name__
        if layer_name in layer_name_map:
            layer_name = layer_name_map[layer_name]

        if config.get_path('kernel_initializer.class_name') == 'VarianceScaling':
            init = str(config.get_path('kernel_initializer.config.distribution', '---'))

        elif config.get_path('kernel_initializer.class_name') == 'RandomUniform':
            init = 'uniform'

        else:
            init = '---'

        output += ui.row(
            layer_name,
            str(layer.output_shape),
            str(layer.count_params()),
            str(layer.name),
            str(connections[0]) if len(connections) > 0 else '---',
            str(config.get('activation', '---')),
            init
        ) + '\n'

    trainable_count = int(
        numpy.sum([keras_backend.count_params(p) for p in set(keras_model.trainable_weights)])
    )

    non_trainable_count = int(
        numpy.sum([keras_backend.count_params(p) for p in set(keras_model.non_trainable_weights)])
    )

    output += ui.line('') + '\n'
    output += ui.line('Parameters') + '\n'
    output += ui.data(indent=4, field='Trainable', value=trainable_count) + '\n'
    output += ui.data(indent=4, field='Non-Trainable', value=non_trainable_count) + '\n'
    output += ui.data(indent=4, field='Total', value=trainable_count + non_trainable_count) + '\n'
    output += ui.line('') + '\n'

    return output


