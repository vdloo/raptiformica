import unittest
from uuid import uuid4

from mock import patch, Mock
from shutil import rmtree

from raptiformica.settings import ABS_CACHE_DIR, PROJECT_DIR
from raptiformica.settings.load import upload_config_mapping
from raptiformica.shell.execute import run_command_print_ready


class TestCase(unittest.TestCase):
    def set_up_patch(self, patch_target, mock_target=None, **kwargs):
        patcher = patch(patch_target, mock_target or Mock(**kwargs))
        self.addCleanup(patcher.stop)
        return patcher.start()


class IntegrationTestCase(TestCase):
    def run_raptiformica_command(self, parameters, buffered=False):
        raptiformica_command = "{}/bin/raptiformica {}".format(
            PROJECT_DIR.rstrip('/'), parameters
        )
        _, standard_out, standard_error = run_command_print_ready(
            raptiformica_command,
            buffered=buffered, shell=True
        )
        return standard_out

    def run_instance_command(self, command_as_string, buffered=False):
        """
        Run a shell command on one of the slaved instances.
        :param str command_as_string: The command to run
        :param bool buffered: Write output to stdout or capture and return it
        :return str output: The buffered output if buffered was True
        """
        raptiformica_command = "`{}/bin/raptiformica ssh --info-only` {}".format(
            PROJECT_DIR.rstrip('/'), command_as_string
        )
        _, standard_out, standard_error = run_command_print_ready(
            raptiformica_command,
            buffered=buffered, shell=True
        )
        return standard_out

    def kill_all_dockers(self):
        kill_all_dockers_command = "sudo docker ps | " \
                                   "grep raptiformica | " \
                                   "awk '{print$1}' | " \
                                   "sudo xargs --no-run-if-empty docker kill"
        run_command_print_ready(
            kill_all_dockers_command,
            buffered=False, shell=True
        )

    def clean_all_docker_images(self):
        clean_all_images_command = "sudo docker images | " \
                                   "grep raptiformica | " \
                                   "awk '{print$3}' | " \
                                   "sudo xargs --no-run-if-empty docker rmi -f"
        run_command_print_ready(
            clean_all_images_command,
            buffered=False, shell=True
        )

    def clean_up_cache_dir(self):
        rmtree(ABS_CACHE_DIR, ignore_errors=True)

    def setUp(self):
        self.kill_all_dockers()
        self.clean_all_docker_images()
        self.clean_up_cache_dir()
        print("Cleaned up any lingering state\n\n")

    def check_consul_consensus_was_established(self, expected_peers=None):
        consul_members_output = self.run_raptiformica_command("members", buffered=True)
        alive_agents = consul_members_output.count("alive")
        if expected_peers is None:
            self.assertGreaterEqual(alive_agents, 3)
        else:
            self.assertEqual(alive_agents, expected_peers)

    def list_registered_peers(self):
        consul_members_output = self.run_instance_command(
            "consul members | grep alive | awk '{print$1}'",
            buffered=True
        )
        return consul_members_output.split()

    def get_docker_ip(self, instance_id):
        get_docker_ip_command = "sudo docker exec {} ip addr show eth0 | " \
                                "grep \"inet\\b\" | " \
                                "awk '{{print $2}}' | " \
                                "cut -d/ -f1"
        _, standard_out, standard_error = run_command_print_ready(
            get_docker_ip_command.format(instance_id),
            buffered=True, shell=True
        )
        return standard_out.strip()

    def list_docker_instances(self):
        list_docker_instances_command = "sudo docker ps | " \
                                        "grep raptiformica | " \
                                        "awk '{print$1}'"
        _, standard_out, standard_error = run_command_print_ready(
            list_docker_instances_command,
            buffered=True, shell=True
        )
        return standard_out.split()

    def check_all_registered_peers_can_be_pinged_from_any_instance(self):
        registered_peers = self.list_registered_peers()
        for registered_peer in registered_peers:
            ret = self.run_instance_command(
                "ping6 {} -c 1".format(registered_peer), buffered=True
            )
            self.assertIn(
                "1 packets transmitted, 1 received", ret,
                "Peer {} could not be pinged from instance".format(
                    registered_peer
                )
            )

    def check_data_can_be_stored_in_the_distributed_kv_store(self):
        expected_value = str(uuid4())
        upload_config_mapping({'test/some/key/in/some/path': expected_value})
        ret = self.run_instance_command(
            '"consul kv get -recurse | grep test"', buffered=True
        )
        self.assertIn(expected_value, ret)

    def tearDown(self):
        print("Finished running this test case, cleaning up the resources\n\n")
        self.kill_all_dockers()
        self.clean_all_docker_images()
        self.clean_up_cache_dir()
