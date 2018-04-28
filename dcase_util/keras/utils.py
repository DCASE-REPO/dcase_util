# !/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import logging
import os
import numpy
import random
from dcase_util.ui import FancyLogger
from dcase_util.utils import SuppressStdoutAndStderr, setup_logging
from dcase_util.decorators import RunOnce

@RunOnce
def setup_keras(seed=None, profile=None,
                backend='theano', device=None,
                BLAS_thread_count=None, BLAS_MKL_CNR=True,
                nvcc_fastmath=None,
                theano_floatX=None, theano_optimizer=None, theano_OpenMP=None, theano_deterministic=None,
                verbose=True, print_indent=0):
    """Setup Keras and environmental variables effecting on it.
    Given parameters are used to override ones specified in keras.json file.

    Parameters
    ----------
    seed : int, optional
        Randomization seed. If none given, no seed is set.
        Default value None

    profile : str, optional
        Profile name ['deterministic', 'cuda0_fast'], will override other parameters with profile parameters.
        Default value None

    backend : str
        Keras backend ['theano', 'tensorflow']
        Default value 'theano'

    device : str, optional
        Device for computations ['cpu', 'cuda', 'cuda0', 'cuda1', 'opencl0:0', 'opencl0:1']
        Default value None

    BLAS_thread_count : int
        Number of thread used for BLAS libraries
        Default value None

    BLAS_MKL_CNR : bool
        Conditional numerical reproducibility for MKL BLAS library. Use this to reproduce results with MKL.
        Default value True

    nvcc_fastmath : str, optional
        Control the usage of fast math library in NVCC
        Default value None

    theano_floatX : str, optional
        Default dtype for Theano matrix and tensor ['float64', 'float32', 'float16']
        Default value None

    theano_optimizer : str, optional
        Optimizer ['fast_run', 'merge', 'fast_compile', 'None']
        Default value None

    theano_OpenMP : bool, optional
        Enable or disable parallel computation on the CPU with OpenMP.
        Default value None

    theano_deterministic : bool, optional
        Default value None

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
            nvcc_fastmath = False
            theano_optimizer = 'None'
            theano_OpenMP = False
            theano_deterministic = True

        elif profile == 'cuda0_fast':
            device = 'cuda0'
            BLAS_thread_count = 8
            BLAS_MKL_CNR = True
            nvcc_fastmath = True
            theano_optimizer = 'fast_run'
            theano_OpenMP = True
            theano_deterministic = True

        else:
            message = 'Invalid Keras setup profile [{profile}].'.format(
                profile=profile
            )
            logger().exception(message)
            raise AttributeError(message)

    # Set seed first
    if seed:
        numpy.random.seed(seed)
        random.seed(seed)

    # Check parameter validity
    if backend and backend not in ['theano', 'tensorflow']:
        message = 'Invalid Keras backend type [{backend}].'.format(
            backend=backend
        )
        logger().exception(message)
        raise AttributeError(message)

    if device and device not in ['cpu', 'cuda', 'cuda0', 'opencl0:0']:
        message = 'Invalid Keras device type [{device}].'.format(
            device=device
        )
        logger().exception(message)
        raise AttributeError(message)

    if theano_floatX and theano_floatX not in ['float64', 'float32', 'float16']:
        message = 'Invalid Keras floatX type [{floatX}].'.format(
            floatX=theano_floatX
        )
        logger().exception(message)
        raise AttributeError(message)

    if theano_optimizer and theano_optimizer not in ['fast_run', 'merge', 'fast_compile', 'None']:
        message = 'Invalid Keras optimizer type [{optimizer}].'.format(
            optimizer=theano_optimizer
        )
        logger().exception(message)
        raise AttributeError(message)

    ui = FancyLogger()
    if verbose:
        ui.sub_header('Keras setup', indent=print_indent)

    # Get BLAS library associated to numpy
    if numpy.__config__.blas_opt_info and 'libraries' in numpy.__config__.blas_opt_info:
        blas_libraries = numpy.__config__.blas_opt_info['libraries']

    else:
        blas_libraries = ['']

    blas_extra_info = []

    # Select Keras backend
    os.environ["KERAS_BACKEND"] = backend

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

    # Set backend and parameters before importing keras
    if verbose:
        ui.data(
            field='Backend',
            value=backend,
            indent=print_indent + 2
        )

    if backend == 'theano':
        # Theano setup

        # Default flags
        flags = [
            # 'ldflags=',
            'warn.round=False',
        ]

        # Set device
        if device:
            flags.append('device=' + device)

        # Set floatX
        if theano_floatX:
            flags.append('floatX=' + theano_floatX)

            if verbose:
                ui.data(
                    field='floatX',
                    value=theano_floatX,
                    indent=print_indent + 2
                )

        # Set optimizer
        if theano_optimizer is not None:
            flags.append('optimizer=' + theano_optimizer)

        # Set fastmath for GPU mode only
        if nvcc_fastmath and device != 'cpu':
            if nvcc_fastmath:
                flags.append('nvcc.fastmath=True')
            else:
                flags.append('nvcc.fastmath=False')

        # Set OpenMP
        if theano_OpenMP is not None:
            if theano_OpenMP:
                flags.append('openmp=True')

            else:
                flags.append('openmp=False')

        if theano_deterministic is not None:
            if theano_deterministic:
                flags.append('deterministic=more')

            else:
                flags.append('deterministic=default')

        if verbose:
            ui.line('Theano', indent=print_indent + 2)

            for item in flags:
                ui.data(
                    field=item.split('=')[0],
                    value=item.split('=')[1],
                    indent=print_indent + 4
                )

        # Set environmental variable for Theano
        os.environ["THEANO_FLAGS"] = ','.join(flags)

    elif backend == 'tensorflow':
        flags = []
        # Tensorflow setup
        if verbose:
            ui.line('Tensorflow', indent=print_indent + 2)

        # Set device
        if device:
            flags.append('device=' + device)

            # In case of CPU disable visible GPU.
            if device == 'cpu':
                os.environ["CUDA_VISIBLE_DEVICES"] = ''

        import tensorflow as tf
        if seed:
            tf.set_random_seed(seed)

        config = tf.ConfigProto(
            inter_op_parallelism_threads=BLAS_thread_count
        )

        from keras import backend as k
        session = tf.Session(config=config)
        k.set_session(session)

        if verbose:
            for item in flags:
                ui.data(
                    field=item.split('=')[0],
                    value=item.split('=')[1],
                    indent=print_indent + 4
                )

    with SuppressStdoutAndStderr():
        # Import keras and suppress backend announcement printed to stderr
        import keras

    if verbose:
        ui.foot(indent=print_indent)


def create_optimizer(class_name, config=None):
    """Create Keras optimizer

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
            importlib.import_module("keras.optimizers"),
            class_name
        )

    except AttributeError:
        message = 'Invalid Keras optimizer type [{type}].'.format(
            type=class_name
        )
        logger().exception(message)
        raise AttributeError(message)

    return optimizer_class(**dict(config))
