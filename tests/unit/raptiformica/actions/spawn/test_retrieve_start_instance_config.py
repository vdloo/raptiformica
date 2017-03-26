from raptiformica.actions.spawn import retrieve_start_instance_config
from tests.testcase import TestCase


class TestRetrieveStartInstanceConfig(TestCase):
    def setUp(self):
        self.types_log = self.set_up_patch('raptiformica.settings.types.log')
        self.spawn_log = self.set_up_patch('raptiformica.actions.spawn.log')
        self.get_config_mapping = self.set_up_patch('raptiformica.actions.spawn.get_config_mapping')
        self.mapping = {
            "raptiformica/compute/docker/headless/available": "docker -v",
            "raptiformica/compute/docker/headless/clean_up_instance_command": "bash -c 'cd ubuntu64 && [ -f container_id ] && cat container_id | xargs sudo docker rm -f || /bin/true'",
            "raptiformica/compute/docker/headless/detect_stale_instance": "bash -c 'cd ubuntu64 && [ -f container_id ] && sudo docker ps --no-trunc | grep -f container_id'",
            "raptiformica/compute/docker/headless/get_hostname": "bash -c \"sudo docker inspect -f '{{ .NetworkSettings.IPAddress }}' $(cat ubuntu64/container_id)\" | tail -n 1",
            "raptiformica/compute/docker/headless/get_port": "echo 22",
            "raptiformica/compute/docker/headless/source": "https://github.com/vdloo/dockerfiles",
            "raptiformica/compute/docker/headless/start_instance": "cd ubuntu64 && chmod 0600 insecure_key && ssh-add insecure_key && sudo docker build -t raptiformica-baseimage . && sudo docker run --privileged -d raptiformica-baseimage > container_id && sleep 5",
            "raptiformica/compute/vagrant/headless/available": "vagrant -v",
            "raptiformica/compute/vagrant/headless/clean_up_instance_command": "cd headless && vagrant destroy -f",
            "raptiformica/compute/vagrant/headless/detect_stale_instance": "cd headless && vagrant status | grep running",
            "raptiformica/compute/vagrant/headless/get_hostname": "cd headless && vagrant ssh-config | grep HostName | awk '{print $NF}'",
            "raptiformica/compute/vagrant/headless/get_port": "cd headless && vagrant ssh-config | grep Port | awk '{print $NF}'",
            "raptiformica/compute/vagrant/headless/source": "https://github.com/vdloo/vagrantfiles",
            "raptiformica/compute/vagrant/headless/start_instance": "cd headless && vagrant up",
            "raptiformica/server/headless/bootstrap": "./papply.sh manifests/headless.pp",
            "raptiformica/server/headless/name": "puppetfiles",
            "raptiformica/server/headless/source": "https://github.com/vdloo/puppetfiles"
        }
        self.get_config_mapping.return_value = self.mapping

    def test_retrieve_start_instance_config_logs_retrieving_instance_config_message(self):
        retrieve_start_instance_config(server_type='headless', compute_type='vagrant')

        self.assertTrue(self.spawn_log.debug.called)

    def test_retrieve_start_instance_config_returns_start_instance_config_for_server_type(self):
        source, start_instance_command, get_hostname_command, get_port_command = retrieve_start_instance_config(
            server_type='headless', compute_type='vagrant'
        )

        self.assertEqual(source, 'https://github.com/vdloo/vagrantfiles')
        self.assertEqual(start_instance_command, 'cd headless && vagrant up')
        self.assertEqual(get_hostname_command, "cd headless && vagrant ssh-config | grep HostName | awk '{print $NF}'")
        self.assertEqual(get_port_command, "cd headless && vagrant ssh-config | grep Port | awk '{print $NF}'")
