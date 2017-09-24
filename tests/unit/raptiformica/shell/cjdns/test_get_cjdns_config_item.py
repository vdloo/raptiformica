from raptiformica.shell.cjdns import get_cjdns_config_item
from raptiformica.shell.execute import COMMAND_TIMEOUT
from tests.testcase import TestCase


class TestGetCjdnsConfigItem(TestCase):
    def setUp(self):
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output

    def test_get_cjdns_config_item_runs_get_item_command_for_public_key(self):
        get_cjdns_config_item('publicKey', '1.2.3.4', port=2222)

        expected_command = [
            '/usr/bin/env', 'ssh', '-A',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ServerAliveInterval=10',
            '-o', 'ServerAliveCountMax=3',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4', '-p', '2222',
            'python', '-c',
            "\"import json; print(json.loads(open("
            "'/etc/cjdroute.conf').read())['publicKey'])\""
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False,
            timeout=COMMAND_TIMEOUT
        )

    def test_get_cjdns_config_item_runs_get_item_command_for_public_key_if_local(self):
        get_cjdns_config_item('publicKey')

        expected_command = [
            'python', '-c',
            "import json; print(json.loads(open("
            "'/etc/cjdroute.conf').read())['publicKey'])"
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False,
            timeout=COMMAND_TIMEOUT
        )

    def test_get_cjdns_config_item_runs_get_item_command_for_ipv6_address(self):
        get_cjdns_config_item('ipv6', '1.2.3.4', port=2223)

        expected_command = [
            '/usr/bin/env', 'ssh', '-A',
            '-o', 'ConnectTimeout=5',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ServerAliveInterval=10',
            '-o', 'ServerAliveCountMax=3',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'PasswordAuthentication=no',
            'root@1.2.3.4', '-p', '2223',
            'python', '-c',
            "\"import json; print(json.loads(open("
            "'/etc/cjdroute.conf').read())['ipv6'])\""
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False,
            timeout=COMMAND_TIMEOUT
        )

    def test_get_cjdns_config_item_raises_error_if_getting_config_item_failed(self):
        process_output = (1, 'standard out output', 'standard error output')
        self.execute_process.return_value = process_output

        with self.assertRaises(RuntimeError):
            get_cjdns_config_item('publicKey', '1.2.3.4', port=2222)

    def test_get_cjdns_config_item_returns_item(self):
        ret = get_cjdns_config_item('publicKey', '1.2.3.4', port=2222)

        self.assertEqual(ret, 'standard out output')
