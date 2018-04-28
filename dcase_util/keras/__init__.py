# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Keras utilities
===============

Utilities to be used with Keras deep learning library.


Model
:::::

*dcase_util.keras.model.* *

.. autosummary::
    :toctree: generated/

    create_sequential_model
    model_summary_string

Callbacks
:::::::::

Usage example how to use external metrics with the Callback classes provided by the dcase_util:

.. code-block:: python
    :linenos:

    epochs = 100
    batch_size = 256
    loss = 'categorical_crossentropy'
    metrics =  ['categorical_accuracy']
    processing_interval = 1
    manual_update = True
    external_metric_labels={'ER': 'Error rate'}

    callback_list = [
            dcase_util.keras.ProgressLoggerCallback(
                epochs=epochs,
                metric=metrics,
                loss=loss,
                manual_update=manual_update,
                manual_update_interval=processing_interval,
                external_metric_labels=external_metric_labels
            ),
            dcase_util.keras.ProgressPlotterCallback(
                epochs=epochs,
                metric=metrics,
                save=False,
                manual_update=manual_update,
                manual_update_interval=processing_interval,
                external_metric_labels=external_metric_labels
            ),
            dcase_util.keras.StopperCallback(
                epochs=epochs,
                monitor=metric[0],
                manual_update=manual_update,
            ),
            dcase_util.keras.StasherCallback(
                epochs=epochs,
                monitor=metric[0],
                manual_update=manual_update,
            )
        ]

    for epoch_start in range(0, epochs, processing_interval):
        epoch_end = epoch_start + processing_interval

        # Make sure we have only specified amount of epochs
        if epoch_end > epochs:
            epoch_end = epochs

        # Train model
        keras_model.fit(
            x=training_X,
            y=training_Y,
            validation_data=(validation_X, validation_Y),
            callbacks=callback_list,
            verbose=0,
            initial_epoch=epoch_start,
            epochs=epoch_end,
            batch_size=batch_size,
            shuffle=True
        )
        # Calculate external metrics
        ER = 0.0

        # Inject external metric values to the callbacks
        for callback in callback_list:
            if hasattr(callback, 'set_external_metric_value'):
                callback.set_external_metric_value(
                    metric_label='ER',
                    metric_value=ER
                )

        # Manually update callbacks
        for callback in callback_list:
            if hasattr(callback, 'update'):
                callback.update()

        # Check we need to stop training
        stop_training = False
        for callback in callback_list:
            if hasattr(callback, 'stop'):
                if callback.stop():
                    stop_training = True

        if stop_training:
            # Stop the training loop
            break

ProgressLoggerCallback
----------------------

*dcase_util.keras.ProgressLoggerCallback*

Keras callback to store metrics with tqdm progress bar or logging interface. Implements Keras Callback API.

This callback is very similar to standard ``ProgbarLogger`` Keras callback, however it adds support for
logging interface and external metrics (metrics calculated outside Keras training process).

.. autosummary::
    :toctree: generated/

    ProgressLoggerCallback


ProgressPlotterCallback
-----------------------

*dcase_util.keras.ProgressPlotterCallback*

Keras callback to plot progress during the training process and save final progress into figure.
Implements Keras Callback API.

.. autosummary::
    :toctree: generated/

    ProgressPlotterCallback


StopperCallback
---------------

*dcase_util.keras.StopperCallback*

Keras callback to stop training when improvement has not seen in specified amount of epochs.
Implements Keras Callback API.

This Callback is very similar to standard ``EarlyStopping`` Keras callback, however it adds support for
external metrics (metrics calculated outside Keras training process).

.. autosummary::
    :toctree: generated/

    StopperCallback


StasherCallback
---------------

*dcase_util.keras.StasherCallback*

Keras callback to monitor training process and store best model. Implements Keras Callback API.

This callback is very similar to standard ``ModelCheckpoint`` Keras callback, however it adds support for
external metrics (metrics calculated outside Keras training process).

.. autosummary::
    :toctree: generated/

    StasherCallback


BaseCallback
------------

*dcase_util.keras.BaseCallback*

.. autosummary::
    :toctree: generated/

    BaseCallback

Data processing
:::::::::::::::

KerasDataSequence
-----------------

*dcase_util.keras.get_keras_data_sequence*

KerasDataSequence class should be accessed through getter method to avoid importing Keras when importing dcase_util.
This mechanics allows user to decide when importing the Keras, and set random seeds before this.

.. autosummary::
    :toctree: generated/

    get_keras_data_sequence_class

data_collector
--------------

*dcase_util.keras.data_collector*

.. autosummary::
    :toctree: generated/

    data_collector

Utils
:::::

*dcase_util.keras.utils.* *

.. autosummary::
    :toctree: generated/

    setup_keras
    create_optimizer

"""

from .model import *
from .callbacks import *
from .data import *
from .utils import *

__all__ = [_ for _ in dir() if not _.startswith('_')]
