from mock import Mock, call

from fcntl import LOCK_EX, LOCK_UN
from raptiformica.settings import conf
from raptiformica.settings.load import config_cache_lock
from tests.testcase import TestCase


class TestConfigCacheLock(TestCase):
    def setUp(self):
        self.open = self.set_up_patch('raptiformica.settings.load.open')
        self.open.return_value.__exit__ = lambda a, b, c, d: None
        self.file_handle = Mock()
        self.open.return_value.__enter__ = lambda a: self.file_handle
        self.flock = self.set_up_patch('raptiformica.settings.load.flock')

    def test_config_cache_lock_opens_cache_config_log_with_w_plus(self):
        with config_cache_lock():
            self.open.assert_called_once_with(
                conf().CONFIG_CACHE_LOCK, 'w+'
            )

    def test_config_cache_lock_flock_locks_lock_file_before_context(self):
        self.assertFalse(self.flock.called)
        with config_cache_lock():
            self.flock.assert_called_once_with(self.file_handle, LOCK_EX)

    def test_config_cache_lock_flock_unlocks_file_after_context(self):
        with config_cache_lock():
            self.flock.assert_called_once_with(self.file_handle, LOCK_EX)

        expected_calls = (
            call(self.file_handle, LOCK_EX),
            call(self.file_handle, LOCK_UN)
        )
        self.assertCountEqual(expected_calls, self.flock.mock_calls)
