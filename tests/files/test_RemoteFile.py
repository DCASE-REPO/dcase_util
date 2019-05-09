""" Unit tests for RemoteFile """

import nose.tools
import tempfile
import os
import platform
from dcase_util.files import RemoteFile


def test_RemoteFile():
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt', dir=tempfile.gettempdir(), delete=False)
    try:
        tmp.write('key1\n')
        tmp.write('key2\n')
        tmp.close()

        r = RemoteFile(filename=tmp.name, content_type='documentation')

        nose.tools.eq_(r.local_exists(), True)

        if platform.system() == 'Windows':
            nose.tools.eq_(r.local_bytes, 12)
            nose.tools.eq_(r.local_size_string(), '12 bytes')
            nose.tools.eq_(r.local_md5, 'cd2ebbdc5e817b5f5fe79c38134320e8')

        else:
            nose.tools.eq_(r.local_bytes, 10)
            nose.tools.eq_(r.local_size_string(), '10 bytes')
            nose.tools.eq_(r.local_md5, '2f34a55e73abe0ca5f39c43eed5aef70')

        r = RemoteFile(filename=tmp.name, content_type='documentation')
        nose.tools.eq_(r.is_content_type(content_type='documentation'), True)
        nose.tools.eq_(r.is_content_type(content_type='meta'), False)
        nose.tools.eq_(r.is_content_type(content_type='all'), True)

        r = RemoteFile(filename=tmp.name, content_type=['documentation', 'audio', 'meta'])
        nose.tools.eq_(r.is_content_type(content_type='all'), True)
        nose.tools.eq_(r.is_content_type(content_type='meta'), True)
        nose.tools.eq_(r.is_content_type(content_type='audio'), True)

        r = RemoteFile(filename=tmp.name, content_type=['documentation'])
        nose.tools.eq_(r.is_content_type(content_type=['meta', 'audio']), False)
        nose.tools.eq_(r.is_content_type(content_type=['all']), True)

        r = RemoteFile(filename=tmp.name)
        nose.tools.eq_(r.is_content_type(content_type=['all']), True)

    finally:

        try:
            tmp.close()
            os.unlink(tmp.name)

        except:
            pass

