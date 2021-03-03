# !/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import logging
import os
import numpy
import random
from dcase_util.ui import FancyLogger, FancyHTMLPrinter
from dcase_util.utils import SuppressStdoutAndStderr, setup_logging, is_jupyter
from dcase_util.decorators import RunOnce

@RunOnce
def setup_keras(seed=None, profile=None, device=None,
                BLAS_thread_count=None, BLAS_MKL_CNR=True,
                verbose=True, print_indent=0, **kwargs):
    """Setup tf.keras and environmental variables effecting on it.
    Given parameters are used to override ones specified in keras.json file.

    Parameters
    ----------
    seed : int, optional
        Randomization seed. If none given, no seed is set.
        Default value None

    profile : str, optional
        Profile name ['deterministic', 'cuda0_fast'], will override other parameters with profile parameters.
        Default value None

    device : str, optional
        Device for computations ['cpu', 'cuda', 'cuda0', 'cuda1', 'opencl0:0', 'opencl0:1']
        Default value None

    BLAS_thread_count : int
        Number of thread used for BLAS libraries
        Default value None

    BLAS_MKL_CNR : bool
        Conditional numerical reproducibility for MKL BLAS library. Use this to reproduce results with MKL.
        Default value True

    verbose : bool
        Print information
        Default value True

    print_indent : int
        Print indent
        Default value 0

    """

    def logger():
        logger_instance = logging.getLogger(__name__)
        if not logger_instance.handlers:
            setup_logging()

        return logger_instance

    if profile:
        if profile == 'deterministic':
            if seed is None:
                message = 'You should set randomization seed to get deterministic behaviour.'
                logger().exception(message)
                raise AttributeError(message)

            # Parameters to help to get deterministic results
            device = 'cpu'
            BLAS_thread_count = 1
            BLAS_MKL_CNR = True

        elif profile == 'cpu':
            device = 'cpu'
            BLAS_thread_count = 8
            BLAS_MKL_CNR = True

        elif profile == 'cuda0' or profile == 'cuda0_fast':
            device = 'cuda0'
            BLAS_thread_count = 8
            BLAS_MKL_CNR = True

        else:
            message = 'Invalid tf.keras setup profile [{profile}].'.format(
                profile=profile
            )
            logger().exception(message)
            raise AttributeError(message)

    # Set seed first
    if seed:
        numpy.random.seed(seed)
        random.seed(seed)

    # Check parameter validity
    if device and device not in ['cpu', 'cuda', 'cuda0', 'opencl0:0']:
        message = 'Invalid tf.keras device type [{device}].'.format(
            device=device
        )
        logger().exception(message)
        raise AttributeError(message)

    if is_jupyter():
        ui = FancyHTMLPrinter()

    else:
        ui = FancyLogger()

    if verbose:
        ui.sub_header('tf.keras setup', indent=print_indent)

    # Get BLAS library associated to numpy
    if numpy.__config__.blas_opt_info and 'libraries' in numpy.__config__.blas_opt_info:
        blas_libraries = numpy.__config__.blas_opt_info['libraries']

    else:
        blas_libraries = ['']

    blas_extra_info = []

    # Threading
    if BLAS_thread_count:
        os.environ['GOTO_NUM_THREADS'] = str(BLAS_thread_count)
        os.environ['OMP_NUM_THREADS'] = str(BLAS_thread_count)
        os.environ['MKL_NUM_THREADS'] = str(BLAS_thread_count)
        blas_extra_info.append('Threads[{threads}]'.format(threads=BLAS_thread_count))

        if BLAS_thread_count > 1:
            os.environ['OMP_DYNAMIC'] = 'False'
            os.environ['MKL_DYNAMIC'] = 'False'

        else:
            os.environ['OMP_DYNAMIC'] = 'True'
            os.environ['MKL_DYNAMIC'] = 'True'

    # Conditional Numerical Reproducibility (CNR) for MKL BLAS library
    if BLAS_MKL_CNR and blas_libraries[0].startswith('mkl'):
        os.environ['MKL_CBWR'] = 'COMPATIBLE'
        blas_extra_info.append('MKL_CBWR[{mode}]'.format(mode='COMPATIBLE'))

    # Show BLAS info
    if verbose:
        if numpy.__config__.blas_opt_info and 'libraries' in numpy.__config__.blas_opt_info:
            blas_libraries = numpy.__config__.blas_opt_info['libraries']

            if blas_libraries[0].startswith('openblas'):
                ui.data(
                    field='BLAS library',
                    value='OpenBLAS ({info})'.format(info=', '.join(blas_extra_info)),
                    indent=print_indent + 2
                )

            elif blas_libraries[0].startswith('blas'):
                ui.data(
                    field='BLAS library',
                    value='BLAS/Atlas ({info})'.format(info=', '.join(blas_extra_info)),
                    indent=print_indent + 2
                )

            elif blas_libraries[0].startswith('mkl'):
                ui.data(
                    field='BLAS library',
                    value='MKL ({info})'.format(info=', '.join(blas_extra_info)),
                    indent=print_indent + 2
                )

    # In case of CPU, disable visible GPUs.
    if device == 'cpu':
        os.environ["CUDA_VISIBLE_DEVICES"] = ''

    import tensorflow as tf

    # Tensorflow setup
    if verbose:
        ui.data('Tensorflow', tf.__version__, indent=print_indent + 2)

    if seed:
        # Set random seed
        tf.random.set_seed(seed)

    tf.config.threading.set_inter_op_parallelism_threads(
        num_threads=BLAS_thread_count
    )

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import logging
    logging.getLogger('tensorflow').setLevel(logging.FATAL)

    if verbose:
        gpu_device_found = False
        if device != 'cpu':
            from tensorflow.python.client import device_lib
            for device_candidate in device_lib.list_local_devices():
                if device_candidate.device_type == 'GPU':
                    gpu_device_found = True

            if not gpu_device_found:
                device = 'cpu ({original_device} was set but not found)'.format(original_device=device)

        ui.data(
            field='Device',
            value=device,
            indent=print_indent + 4
        )

    from tensorflow import keras

    if verbose:
        ui.foot(indent=print_indent)


def create_optimizer(class_name, config=None):
    """Create tf.keras optimizer

    Parameters
    ----------

    class_name : str
        Keras optimizer class name under keras.optimizers.*

    config : dict, optional
        Parameters

    Returns
    -------
    Keras optimizer

    """

    def logger():
        logger_instance = logging.getLogger(__name__)
        if not logger_instance.handlers:
            setup_logging()
        return logger_instance

    if config is None:
        config = {}

    # Get optimizer class
    try:
        optimizer_class = getattr(
            importlib.import_module("tensorflow.keras.optimizers"),
            class_name
        )

    except AttributeError:
        message = 'Invalid tf.keras optimizer type [{type}].'.format(
            type=class_name
        )
        logger().exception(message)
        raise AttributeError(message)

    return optimizer_class(**dict(config))
