from raptiformica.shell.compute import compute_attribute_get
from raptiformica.shell.execute import COMMAND_TIMEOUT
from tests.testcase import TestCase


class TestComputeAttributeGet(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.compute.log')
        self.args = (
            '/home/user/code/projects/raptiformica/var/machines/vagrant/b3835ef2f1d7494097facb539c119a31',
            "cd headless && vagrant ssh-config | grep HostName | awk '{print$NF}'",
            'hostname'
        )
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )

        self.process_output = (0, 'standard out output\n', 'standard error output')
        self.execute_process.return_value = self.process_output

    def test_compute_attribute_get_logs_getting_attribute_message(self):
        compute_attribute_get(*self.args)

        self.assertTrue(self.log.info.called)

    def test_compute_attribute_get_runs_get_attribute_command_on_local_host(self):
        compute_attribute_get(*self.args)

        expected_command = [
            'sh', '-c', "cd /home/user/code/projects/raptiformica/var/machines"
                        "/vagrant/b3835ef2f1d7494097facb539c119a31; cd headless "
                        "&& vagrant ssh-config | grep HostName | awk '{print$NF}'"
        ]
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=True,
            shell=False,
            timeout=COMMAND_TIMEOUT
        )

    def test_compute_attribute_get_returns_stripped_standard_out(self):
        ret = compute_attribute_get(*self.args)

        self.assertEqual(ret, 'standard out output')

    def test_compute_attribute_get_raises_error_when_command_failed(self):
        self.process_output = (1, '', 'standard error output')
        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            compute_attribute_get(*self.args)
