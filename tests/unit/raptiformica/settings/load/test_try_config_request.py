from mock import Mock, call
from urllib.error import HTTPError

from raptiformica.settings import conf
from raptiformica.settings.load import try_config_request
from tests.testcase import TestCase


class TestTryConfigRequest(TestCase):
    def setUp(self):
        self.callback = Mock()
        self.forward_any_port = self.set_up_patch(
            'raptiformica.distributed.proxy.forward_any_port'
        )
        self.forward_any_port.return_value.__exit__ = lambda a, b, c, d: None
        self.forward_any_port.return_value.__enter__ = lambda a: None
        conf().FORWARDED_CONSUL_ONCE_ALREADY = False

    def test_try_config_request_performs_callback(self):
        try_config_request(self.callback)

        self.callback.assert_called_once_with()

    def test_try_config_request_returns_callback_result(self):
        ret = try_config_request(self.callback)

        self.assertEqual(ret, self.callback.return_value)

    def test_try_config_request_does_not_forward_any_ports_when_successful(self):
        try_config_request(self.callback)

        self.assertFalse(self.forward_any_port.called)

    def test_try_config_request_forwards_remote_port_if_local_api_call_fails(self):
        self.callback.side_effect = [
            HTTPError('url', 'code', 'msg', 'hdrs', Mock()),
            Mock()
        ]
        try_config_request(self.callback)

        self.forward_any_port.assert_called_once_with(
            source_port=8500,
            predicate=[
                'consul', 'kv', 'get', '/raptiformica/raptiformica_api_version'
            ]
        )

    def test_try_config_request_does_not_forward_remote_port_if_already_forwarded_once_before(self):
        conf().set_forwarded_remote_consul_once()

        self.callback.side_effect = [
            HTTPError('url', 'code', 'msg', 'hdrs', Mock()),
            Mock()
        ]
        with self.assertRaises(HTTPError):
            try_config_request(self.callback)

    def test_try_config_request_tries_callback_again_with_forwarded_port(self):
        self.callback.side_effect = [
            HTTPError('url', 'code', 'msg', 'hdrs', Mock()),
            Mock()
        ]

        try_config_request(self.callback)

        expected_calls = (call(), call())
        self.assertCountEqual(self.callback.mock_calls, expected_calls)

    def test_try_config_request_returns_second_attempt_result(self):
        expected_result = Mock()
        self.callback.side_effect = [
            HTTPError('url', 'code', 'msg', 'hdrs', Mock()),
            expected_result
        ]

        ret = try_config_request(self.callback)

        self.assertEqual(ret, expected_result)

    def test_try_config_request_raises_error_if_second_attempt_failed_as_well(self):
        self.callback.side_effect = [
            HTTPError('url', 'code', 'msg', 'hdrs', Mock()),
            HTTPError('url', 'code', 'msg', 'hdrs', Mock()),
        ]

        with self.assertRaises(HTTPError):
            try_config_request(self.callback)
