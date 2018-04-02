.. _library:

Library
-------

`dcase_util` is a collection of utility classes and function implemented to streamline the research code,
make it more readable, and easier to maintain. Most of the implemented utilities are related to audio datasets:
handling meta data and various forms of other structured data, and provide standardize usage API to
audio datasets from various sources.

Design principles:

- Concentrate on common utilities needed for DCASE research and DCASE challenge organization.
- Use object-oriented design when applicable.
- Design class APIs to allow class extension through class inheritance.
- Wrap data into container classes, inherit containers from standard Python containers when possible to keep code usable with external tools.
- Favor readable code over highly optimized code, avoid one-liners or hackish code.
- In case of inherited classes, expose all valid parameters as args in the function definition and inject them back to kwargs for the super classes.
- Enable chaining class method calls by returning self when possible.
- Use extensive code commenting.
- Validate code through unit-testing.
- Follow PEP 8 style guide.

Author
======

Initial version was written by Toni Heittola (`Audio Research Group / Tampere University of Technology <http://arg.cs.tut.fi/>`_) while preparing `DCASE2016 Challenge <https://github.com/TUT-ARG/DCASE2016-baseline-system-python>`_ and `DCASE2017 Challenge <https://github.com/TUT-ARG/DCASE2017-baseline-system>`_. Contact via `website <http://www.cs.tut.fi/~heittolt/>`_ and `github <https://github.com/toni-heittola>`_.


Contributing
============

In case you find bugs, stumble on errors while using the utilities, come up things which needs improvement or have an idea of new utilities, please create an issue or a pull request at https://github.com/DCASE-REPO/dcase_util/. All contributions are always welcomed!

Testing
:::::::

If you fix a bug, you should also add a unit test that exposes the bug to avoid similar bugs in the future revisions. If you add a new feature, you should add test for it as well.

To run the tests, use::

    python setup.py nosetests


After running tests, the coverage report is located at `tests/cover/index.html`

Tests are located in directory `tests`.

Documentation
:::::::::::::

If you make changes to the documentation, you can re-create the HTML pages on your local system using Sphinx.

You can install it and a few other necessary packages with::

    pip install -r documentation/requirements.txt --user

To create the HTML pages, use::

    python setup.py build_sphinx


The generated files will be available in the directory `docs`