from mock import call

from raptiformica.settings import INSTALL_DIR, MUTABLE_CONFIG, ABS_CACHE_DIR
from raptiformica.settings import PROJECT_DIR
from raptiformica.shell.rsync import upload_self
from tests.testcase import TestCase


class TestUploadSelf(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.rsync.log')
        self.upload = self.set_up_patch(
            'raptiformica.shell.rsync.upload', return_value=0
        )
        self.create_remote_raptiformica_cache = self.set_up_patch(
            'raptiformica.shell.rsync.create_remote_raptiformica_cache',
            return_value=0
        )
        self.create_remote_raptiformica_cache.return_value = 0
        self.isdir = self.set_up_patch(
            'raptiformica.shell.rsync.isdir',
            return_value=True
        )

    def test_upload_self_logs_uploading_self_message(self):
        upload_self('1.2.3.4', port=22)

        self.assertTrue(self.log.info.called)

    def test_upload_self_uploads_project(self):
        upload_self('1.2.3.4', port=22)

        expected_calls = [
            call(PROJECT_DIR, INSTALL_DIR, host='1.2.3.4', port=22),
            call(ABS_CACHE_DIR, "$HOME", host='1.2.3.4', port=22)
        ]
        self.assertCountEqual(self.upload.mock_calls, expected_calls)

    def test_upload_self_creates_remote_raptiformica_cache_directory(self):
        upload_self('1.2.3.4', port=22)

        self.create_remote_raptiformica_cache.assert_called_once_with(
            '1.2.3.4', port=22
        )

    def test_upload_self_returns_true_if_success(self):
        ret = upload_self('1.2.3.4', port=22)

        self.assertTrue(ret)

    def test_upload_returns_false_if_project_upload_fails(self):
        self.upload.side_effect = [1, 0]

        ret = upload_self('1.2.3.4', port=22)

        self.assertFalse(ret)

    def test_upload_returns_false_if_creating_remote_cache_directory_failed(self):
        self.create_remote_raptiformica_cache.return_value = 1

        ret = upload_self('1.2.3.4', port=22)

        self.assertFalse(ret)

    def test_upload_returns_false_if_syncing_mutable_config_failed(self):
        self.upload.side_effect = [0, 1]

        ret = upload_self('1.2.3.4', port=22)

        self.assertFalse(ret)
