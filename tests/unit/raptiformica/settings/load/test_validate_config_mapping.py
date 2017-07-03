from raptiformica.settings.load import validate_config_mapping
from tests.testcase import TestCase


class TestValidateConfigMapping(TestCase):
    def setUp(self):
        self.mapping = {
            "raptiformica/compute/vagrant/headless/get_port": "cd headless && vagrant ssh-config | grep Port | awk '{print $NF}'",
            "raptiformica/server/headless/puppetfiles/bootstrap": "./papply.sh manifests/headless.pp",
            "raptiformica/platform/default/hooks/after_assimilate/notify_assimilate_instance/command": "/bin/true",
            "raptiformica/meshnet/neighbours/w8qtgm7wc93gbd4pzm7zg8vhgvcqn4x3qwgd23u99kuxlcr7dh60.k/cjdns_ipv6_address": "fcac:f6e3:a8d4:10f:5b22:111f:9b9:956d",
        }

    def test_validate_config_mapping_returns_true_if_config_valid(self):
        ret = validate_config_mapping(self.mapping)

        self.assertTrue(ret)

    def test_validate_config_mapping_returns_false_if_compute_section_is_missing(self):
        missing_compute_mapping = {
            "raptiformica/server/headless/puppetfiles/bootstrap": "./papply.sh manifests/headless.pp",
            "raptiformica/platform/default/hooks/after_assimilate/notify_assimilate_instance/command": "/bin/true",
            "raptiformica/meshnet/neighbours/w8qtgm7wc93gbd4pzm7zg8vhgvcqn4x3qwgd23u99kuxlcr7dh60.k/cjdns_ipv6_address": "fcac:f6e3:a8d4:10f:5b22:111f:9b9:956d",
        }

        ret = validate_config_mapping(missing_compute_mapping)

        self.assertFalse(ret)

    def test_validate_config_mapping_returns_false_if_server_section_is_missing(self):
        missing_compute_mapping = {
            "raptiformica/compute/vagrant/headless/get_port": "cd headless && vagrant ssh-config | grep Port | awk '{print $NF}'",
            "raptiformica/platform/default/hooks/after_assimilate/notify_assimilate_instance/command": "/bin/true",
            "raptiformica/meshnet/neighbours/w8qtgm7wc93gbd4pzm7zg8vhgvcqn4x3qwgd23u99kuxlcr7dh60.k/cjdns_ipv6_address": "fcac:f6e3:a8d4:10f:5b22:111f:9b9:956d",
        }

        ret = validate_config_mapping(missing_compute_mapping)

        self.assertFalse(ret)

    def test_validate_config_mapping_returns_false_if_platform_section_is_missing(self):
        missing_compute_mapping = {
            "raptiformica/compute/vagrant/headless/get_port": "cd headless && vagrant ssh-config | grep Port | awk '{print $NF}'",
            "raptiformica/server/headless/puppetfiles/bootstrap": "./papply.sh manifests/headless.pp",
            "raptiformica/meshnet/neighbours/w8qtgm7wc93gbd4pzm7zg8vhgvcqn4x3qwgd23u99kuxlcr7dh60.k/cjdns_ipv6_address": "fcac:f6e3:a8d4:10f:5b22:111f:9b9:956d",
        }

        ret = validate_config_mapping(missing_compute_mapping)

        self.assertFalse(ret)
