""" Test functions in util
"""

import re

from unittest.mock import patch

from meshtastic_flasher.util import (get_path, populate_tag_in_firmware_dropdown,
                                     tag_to_version, tags_to_versions, get_tags,
                                     download_if_zip_does_not_exist, unzip_if_necessary,
                                     check_if_newer_version, zero_if_blank)


def test_get_path():
    """Test get_path()"""
    assert get_path("foo.file").endswith("foo.file")
    assert len(get_path("foo.file")) > 10


def test_populate_tag_in_firmware_dropdown():
    """Test populate_tag_in_firmware_dropdown()"""
    assert populate_tag_in_firmware_dropdown("v1.2.60.foo")
    assert populate_tag_in_firmware_dropdown("v1.2.52.foo")
    assert populate_tag_in_firmware_dropdown("v1.2.51.foo")


def test_tag_to_version():
    """Test tag to version"""
    assert tag_to_version('') == ''
    assert tag_to_version('v123') == '123'
    assert tag_to_version('123') == '123'


def test_tags_to_versions():
    """Test tags to versions"""
    assert not tags_to_versions([])
    assert tags_to_versions(['v123','v234']) == ['123', '234']
    assert tags_to_versions(['123','234']) == ['123', '234']


@patch('meshtastic_flasher.util.get_tags_from_github', return_value=[])
def test_get_tags_got_no_tags(fake_get_tags):
    """Test get_tags() when we got no tags"""
    tags = get_tags()
    assert len(tags) == 1
    fake_get_tags.assert_called()


@patch('meshtastic_flasher.util.get_tags_from_github', return_value=['v1.2.53aa', 'v1.2.53fff', 'v1.2.51f'])
def test_get_tags_got_some_tags(fake_get_tags):
    """Test get_tags() when we got some tags"""
    tags = get_tags()
    assert len(tags) == 3
    fake_get_tags.assert_called()


@patch('urllib.request.urlretrieve')
@patch('os.path.exists', return_value=False)
def test_download_if_zip_does_not_exist(patched_exists, patched_url, capsys):
    """Test download_if_zip_does_not_exist()"""

    download_if_zip_does_not_exist('foo.zip', '1.2.3')

    out, err = capsys.readouterr()
    assert re.search(r'Need to download', out, re.MULTILINE)
    assert re.search(r'done downloading', out, re.MULTILINE)
    assert err == ''
    patched_exists.assert_called()
    patched_url.assert_called()


@patch('urllib.request.urlretrieve')
@patch('os.path.exists', return_value=False)
def test_download_if_zip_does_not_exist_when_exception_with_urllib(patched_exists, patched_url, capsys):
    """Test download_if_zip_does_not_exist()"""

    def throw_an_exception(junk):
        raise Exception("Fake exception.")

    patched_url.side_effect = throw_an_exception

    download_if_zip_does_not_exist('foo.zip', '1.2.3')

    out, err = capsys.readouterr()
    assert re.search(r'could not download', out, re.MULTILINE)
    assert err == ''
    patched_exists.assert_called()
    patched_url.assert_called()


@patch('zipfile.ZipFile')
@patch('os.path.exists', side_effect=[False, True])
def test_unzip_if_necessary(patched_exists, patched_zipfile, capsys):
    """Test unzip_if_necessary()"""

    unzip_if_necessary('1.2.3', 'foo.zip')

    out, err = capsys.readouterr()
    assert re.search(r'Unzipping files', out, re.MULTILINE)
    assert err == ''
    patched_exists.assert_called()
    patched_zipfile.assert_called()


@patch('requests.get')
def test_check_if_newer_version_when_current(patched_requests_get):
    """Test check_if_newer_version()"""

    patched_requests_get().json.return_value = {
            "info": {
                "version": "1.2.3"
                }
            }

    with patch('meshtastic_flasher.version.__version__', '1.2.3'):
        result = check_if_newer_version()
        assert result is False


@patch('requests.get')
def test_check_if_newer_version_when_not_current(patched_requests_get):
    """Test check_if_newer_version()"""

    patched_requests_get().json.return_value = {
            "info": {
                "version": "1.2.4"
                }
            }

    with patch('meshtastic_flasher.version.__version__', '1.2.3'):
        result = check_if_newer_version()
        assert result is True


@patch('requests.get')
def test_check_if_newer_version_when_problem_getting_pypi(patched_requests_get):
    """Test check_if_newer_version()"""

    patched_requests_get().json.return_value = {}

    with patch('meshtastic_flasher.version.__version__', '1.2.3'):
        result = check_if_newer_version()
        assert result is False


def test_zero_if_blank():
    """Test zero_if_blank()"""
    assert zero_if_blank("") == "0"
    assert zero_if_blank("0") == "0"
    assert zero_if_blank("1") == "1"
    assert zero_if_blank("1.1") == "1.1"
