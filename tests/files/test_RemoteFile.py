""" Unit tests for RemoteFile """
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

        assert r.local_exists() == True

        if platform.system() == 'Windows':
            assert r.local_bytes == 12
            assert r.local_size_string() == '12 bytes'
            assert r.local_md5 == 'cd2ebbdc5e817b5f5fe79c38134320e8'

        else:
            assert r.local_bytes == 10
            assert r.local_size_string() == '10 bytes'
            assert r.local_md5 == '2f34a55e73abe0ca5f39c43eed5aef70'

        r = RemoteFile(filename=tmp.name, content_type='documentation')
        assert r.is_content_type(content_type='documentation') == True
        assert r.is_content_type(content_type='meta') == False
        assert r.is_content_type(content_type='all') == True

        r = RemoteFile(filename=tmp.name, content_type=['documentation', 'audio', 'meta'])
        assert r.is_content_type(content_type='all') == True
        assert r.is_content_type(content_type='meta') == True
        assert r.is_content_type(content_type='audio') == True

        r = RemoteFile(filename=tmp.name, content_type=['documentation'])
        assert r.is_content_type(content_type=['meta', 'audio']) == False
        assert r.is_content_type(content_type=['all']) == True

        r = RemoteFile(filename=tmp.name)
        assert r.is_content_type(content_type=['all']) == True

    finally:

        try:
            tmp.close()
            os.unlink(tmp.name)

        except:
            pass

