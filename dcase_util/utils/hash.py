#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import hashlib
import json


def get_parameter_hash(params):
    """Get unique hash string (md5) for given parameter dict

    Parameters
    ----------
    params : dict, list
        Input parameters

    Returns
    -------
    str
        Unique hash for parameter dict

    """

    md5 = hashlib.md5()
    md5.update(str(json.dumps(params, sort_keys=True)).encode('utf-8'))

    return md5.hexdigest()


def get_file_hash(filename):
    """Get unique hash string (md5) for given file

    Parameters
    ----------
    filename : str
        File path

    Returns
    -------
    str
        Unique hash for parameter dict

    """

    md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)

    return md5.hexdigest()
