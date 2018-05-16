.. _installation:

Installation instructions
-------------------------

PyPI
====

The latest stable release is available on PyPI, and you can install with pip::

    pip install dcase_util


Source
======


Alternatively you can download or clone library and use ``pip`` to handle dependencies::

    unzip dcase_util.zip
    pip install -e dcase_util

or::

    git clone https://github.com/DCASE-REPO/dcase_util.git
    pip install -e dcase_util

To install library for the development, use::

    python setup.py develop


Dependencies
============

In order to keep dependencies of ``dcase_util`` light, not all external libraries are installed automatically.
Dependencies needed for more rarely needed functionality is left out, and they need to be installed manually.
User will be instructed to install external libraries once they are needed.
You can install all needed libraries by running::

    pip install -r requirements.txt

