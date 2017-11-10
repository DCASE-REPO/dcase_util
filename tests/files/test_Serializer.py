""" Unit tests for RemoteFile """

import nose.tools
import tempfile
import os
from dcase_util.files import Serializer


def test_Serializer():
    data = {
        'field1': 10,
        'field2': 100,
        'field3': 1000,
    }

    s = Serializer()
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.yaml', dir='/tmp', delete=False)
    try:
        s.save_yaml(filename=tmp.name, data=data)
        nose.tools.eq_(data, s.load_yaml(filename=tmp.name))
    finally:
        os.unlink(tmp.name)

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.cpickle', dir='/tmp', delete=False)
    try:
        s.save_cpickle(filename=tmp.name, data=data)
        nose.tools.eq_(data, s.load_cpickle(filename=tmp.name))
    finally:
        os.unlink(tmp.name)

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.json', dir='/tmp', delete=False)
    try:
        s.save_json(filename=tmp.name, data=data)
        nose.tools.eq_(data, s.load_json(filename=tmp.name))
    finally:
        os.unlink(tmp.name)

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.msgpack', dir='/tmp', delete=False)
    try:
        s.save_msgpack(filename=tmp.name, data=data)
        nose.tools.eq_(data, s.load_msgpack(filename=tmp.name))
    finally:
        os.unlink(tmp.name)

    tmp = tempfile.NamedTemporaryFile('r+', suffix='.marshal', dir='/tmp', delete=False)
    try:
        s.save_marshal(filename=tmp.name, data=data)
        nose.tools.eq_(data, s.load_marshal(filename=tmp.name))
    finally:
        os.unlink(tmp.name)
