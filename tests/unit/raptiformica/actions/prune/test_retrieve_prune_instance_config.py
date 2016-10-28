from raptiformica.actions.prune import retrieve_prune_instance_config
from tests.testcase import TestCase


class TestRetrievePruneInstanceConfig(TestCase):
    def setUp(self):
        self.types_log = self.set_up_patch('raptiformica.settings.types.log')
        self.prune_log = self.set_up_patch('raptiformica.actions.prune.log')
        self.mapping = {
            "raptiformica/compute/docker/headless/available": "docker -v",
            "raptiformica/compute/docker/headless/clean_up_instance_command": "bash -c 'cd ubuntu64 && [ -f container_id ] && cat container_id | xargs sudo docker rm -f || /bin/true'",
            "raptiformica/compute/docker/headless/detect_stale_instance": "bash -c 'cd ubuntu64 && [ -f container_id ] && sudo docker ps --no-trunc | grep -f container_id'",
            "raptiformica/compute/docker/headless/get_hostname": "bash -c \"sudo docker inspect -f '{{ .NetworkSettings.IPAddress }}' $(cat ubuntu64/container_id)\" | tail -n 1",
            "raptiformica/compute/docker/headless/get_port": "echo 22",
            "raptiformica/compute/docker/headless/source": "https://github.com/vdloo/dockerfiles.git",
            "raptiformica/compute/docker/headless/start_instance": "cd ubuntu64 && chmod 0600 insecure_key && ssh-add insecure_key && sudo docker build -t raptiformica-baseimage . && sudo docker run --privileged -d raptiformica-baseimage > container_id && sleep 5",
            "raptiformica/compute/vagrant/headless/available": "vagrant -v",
            "raptiformica/compute/vagrant/headless/clean_up_instance_command": "cd headless && vagrant destroy -f",
            "raptiformica/compute/vagrant/headless/detect_stale_instance": "cd headless && vagrant status | grep running",
            "raptiformica/compute/vagrant/headless/get_hostname": "cd headless && vagrant ssh-config | grep HostName | awk '{print $NF}'",
            "raptiformica/compute/vagrant/headless/get_port": "cd headless && vagrant ssh-config | grep Port | awk '{print $NF}'",
            "raptiformica/compute/vagrant/headless/source": "https://github.com/vdloo/vagrantfiles.git",
            "raptiformica/compute/vagrant/headless/start_instance": "cd headless && vagrant up",
        }
        self.get_config_mapping = self.set_up_patch('raptiformica.settings.load.get_config_mapping')
        self.get_config_mapping.return_value = self.mapping

    def test_retrieve_prune_instance_config_logs_retrieving_instance_config_message(self):
        retrieve_prune_instance_config(server_type='headless', compute_type='docker')

        self.assertTrue(self.prune_log.debug.called)

    def test_retrieve_prune_instance_config_raises_runtimeerror_when_server_type_not_in_compute_config(self):
        with self.assertRaises(RuntimeError):
            retrieve_prune_instance_config(server_type='doesnotexist', compute_type='docker')

    def test_retrieve_prune_instance_config_returns_prune_instance_config_for_server_type(self):
        detect_stale_instance_command, clean_up_instance_command = retrieve_prune_instance_config(
            server_type='headless', compute_type='docker'
        )

        self.assertEqual(
            detect_stale_instance_command,
            "bash -c 'cd ubuntu64 && [ -f container_id ] && sudo docker ps --no-trunc | grep -f container_id'"
        )
        self.assertEqual(
            clean_up_instance_command,
            "bash -c 'cd ubuntu64 && [ -f container_id ] && cat container_id | xargs sudo docker rm -f || /bin/true'"
        )
