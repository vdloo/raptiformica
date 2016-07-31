from raptiformica.shell.compute import boot_instance
from tests.testcase import TestCase


class TestBootInstance(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.compute.log')
        self.args = (
            '/home/user/code/projects/raptiformica/var/machines/vagrant/b3835ef2f1d7494097facb539c119a31',
            "cd headless && vagrant up --provider=virtualbox"
        )
        self.execute_process = self.set_up_patch(
            'raptiformica.shell.execute.execute_process'
        )

        self.process_output = (0, 'standard out output', 'standard error output')
        self.execute_process.return_value = self.process_output

    def test_boot_instance_logs_booting_new_instance_message(self):
        boot_instance(*self.args)

        self.assertTrue(self.log.info.called)

    def test_boot_instance_runs_boot_instance_command_on_local_host(self):
        boot_instance(*self.args)

        expected_command = ['sh', '-c', 'cd /home/user/code/projects/'
                                        'raptiformica/var/machines/'
                                        'vagrant/b3835ef2f1d7494097facb539c119a31; '
                                        'cd headless && vagrant up '
                                        '--provider=virtualbox']
        self.execute_process.assert_called_once_with(
            expected_command,
            buffered=False,
            shell=False
        )

    def test_boot_instance_raises_error_when_command_failed(self):
        self.process_output = (1, '', 'standard error output')

        self.execute_process.return_value = self.process_output

        with self.assertRaises(RuntimeError):
            boot_instance(*self.args)

    def test_boot_instance_returns_command_exit_code(self):
        ret = boot_instance(*self.args)

        self.assertEqual(ret, 0)
