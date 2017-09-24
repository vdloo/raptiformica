import socket
from urllib.error import URLError, HTTPError

from mock import Mock

from raptiformica.settings.load import try_update_config_mapping
from tests.testcase import TestCase


class TestTryUpdateConfig(TestCase):
    def setUp(self):
        self.mapping = {
            'some/key': 'value',
            'some/other/key': 'other_value'
        }
        self.update_config = self.set_up_patch(
            'raptiformica.settings.load.update_config_mapping'
        )
        self.get_config = self.set_up_patch(
            'raptiformica.settings.load.get_config_mapping'
        )
        self.cache_config = self.set_up_patch(
            'raptiformica.settings.load.cache_config_mapping'
        )

    def test_try_update_config_updates_config_with_mapping(self):
        try_update_config_mapping(self.mapping)

        self.update_config.assert_called_once_with(
            self.mapping
        )

    def test_try_update_config_gets_config_if_http_error(self):
        self.update_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        try_update_config_mapping(self.mapping)

        self.get_config.assert_called_once_with()

    def test_try_update_config_gets_config_if_url_error(self):
        self.update_config.side_effect = URLError('reason')

        try_update_config_mapping(self.mapping)

        self.get_config.assert_called_once_with()

    def test_try_update_config_gets_config_if_connection_refused_error(self):
        self.update_config.side_effect = ConnectionRefusedError

        try_update_config_mapping(self.mapping)

        self.get_config.assert_called_once_with()

    def test_try_update_config_updates_cached_mapping_if_http_error(self):
        self.update_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        try_update_config_mapping(self.mapping)

        self.get_config.return_value.update.assert_called_once_with(
            self.mapping
        )

    def test_try_update_config_updates_cached_mapping_if_url_error(self):
        self.update_config.side_effect = URLError('reason')

        try_update_config_mapping(self.mapping)

        self.get_config.return_value.update.assert_called_once_with(
            self.mapping
        )

    def test_try_update_config_updates_cached_mapping_if_connection_refused_error(self):
        self.update_config.side_effect = ConnectionRefusedError

        try_update_config_mapping(self.mapping)

        self.get_config.return_value.update.assert_called_once_with(
            self.mapping
        )

    def test_try_update_config_updates_cached_mapping_if_socket_timeout(self):
        self.update_config.side_effect = socket.timeout

        try_update_config_mapping(self.mapping)

        self.get_config.return_value.update.assert_called_once_with(
            self.mapping
        )

    def test_try_update_config_caches_updated_mapping_if_http_error(self):
        self.update_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        try_update_config_mapping(self.mapping)

        self.cache_config.assert_called_once_with(
            self.get_config.return_value
        )

    def test_try_update_config_caches_updated_mapping_if_url_error(self):
        self.update_config.side_effect = URLError('reason')

        try_update_config_mapping(self.mapping)

        self.cache_config.assert_called_once_with(
            self.get_config.return_value
        )

    def test_try_update_config_caches_updated_mapping_if_connection_refused_error(self):
        self.update_config.side_effect = ConnectionRefusedError

        try_update_config_mapping(self.mapping)

        self.cache_config.assert_called_once_with(
            self.get_config.return_value
        )

    def test_try_update_config_returns_mapping(self):
        ret = try_update_config_mapping(self.mapping)

        self.assertEqual(self.update_config.return_value, ret)

    def test_try_update_config_returns_cached_mapping_if_http_error(self):
        self.update_config.side_effect = HTTPError('url', 'code', 'msg', 'hdrs', Mock())

        ret = try_update_config_mapping(self.mapping)

        self.assertEqual(self.get_config.return_value, ret)

    def test_try_update_config_returns_cached_mapping_if_url_error(self):
        self.update_config.side_effect = URLError('reason')

        ret = try_update_config_mapping(self.mapping)

        self.assertEqual(self.get_config.return_value, ret)

    def test_try_update_config_returns_cached_mapping_if_connection_refused_error(self):
        self.update_config.side_effect = ConnectionRefusedError

        ret = try_update_config_mapping(self.mapping)

        self.assertEqual(self.get_config.return_value, ret)
