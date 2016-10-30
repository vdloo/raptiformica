from mock import call

from raptiformica.shell.cjdns import ensure_cjdns_dependencies
from tests.testcase import TestCase


class TestEnsureCjdnsDependencies(TestCase):
    def setUp(self):
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )
        self.process_output = (0, 'standard out output', '')
        self.execute_process.return_value = self.process_output
        self.maxDiff = None

    def test_ensure_cjdns_dependencies_tries_commands_for_all_supported_distros(self):
        ensure_cjdns_dependencies('1.2.3.4', port=2222)

        expected_archlinux_call = call(
            '/usr/bin/env ssh '
            '-o ConnectTimeout=5 '
            '-o StrictHostKeyChecking=no '
            '-o UserKnownHostsFile=/dev/null '
            '-o PasswordAuthentication=no '
            'root@1.2.3.4 -p 2222 \''
            'type pacman 1> /dev/null && '
            'pacman -S --noconfirm nodejs base-devel --needed '
            '|| /bin/true'
            '\'',
            buffered=False, shell=True
        )
        expected_debian_call = call(
            '/usr/bin/env ssh '
            '-o ConnectTimeout=5 '
            '-o StrictHostKeyChecking=no '
            '-o UserKnownHostsFile=/dev/null '
            '-o PasswordAuthentication=no '
            'root@1.2.3.4 -p 2222 \''
            'type apt-get 1> /dev/null && '
            'apt-get install -yy nodejs '
            'build-essential git python '
            '|| /bin/true'
            '\'',
            buffered=False, shell=True
        )
        expected_calls = [expected_archlinux_call, expected_debian_call]
        self.assertCountEqual(expected_calls, self.execute_process.mock_calls)

    def test_ensure_cjdns_dependencies_tries_commands_on_local_machine_if_no_host(self):
        ensure_cjdns_dependencies()

        expected_archlinux_call = call(
            'type pacman 1> /dev/null && '
            'pacman -S --noconfirm nodejs base-devel --needed '
            '|| /bin/true',
            buffered=False, shell=True
        )
        expected_debian_call = call(
            'type apt-get 1> /dev/null && '
            'apt-get install -yy nodejs '
            'build-essential git python '
            '|| /bin/true',
            buffered=False, shell=True
        )
        expected_calls = [expected_archlinux_call, expected_debian_call]
        self.assertCountEqual(expected_calls, self.execute_process.mock_calls)

    def test_ensure_cjdns_dependencies_raises_error_when_the_first_command_fails(self):
        self.execute_process.side_effect = [(1, 'standard out output', ''), self.process_output]

        with self.assertRaises(RuntimeError):
            ensure_cjdns_dependencies('1.2.3.4', port=2222)

        self.assertEqual(1, len(self.execute_process.mock_calls))

    def test_ensure_cjdns_dependencies_raises_error_when_the_second_command_fails(self):
        self.execute_process.side_effect = [self.process_output, (1, 'standard out output', '')]

        with self.assertRaises(RuntimeError):
            ensure_cjdns_dependencies('1.2.3.4', port=2222)

        self.assertEqual(2, len(self.execute_process.mock_calls))
