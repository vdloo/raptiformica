from mock import call

from raptiformica.actions.mesh import configure_consul_conf, CJDROUTE_CONF_PATH, CONSUL_CONF_PATH
from tests.testcase import TestCase


class TestConfigureConsulConf(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.mesh.log')
        self.gethostname = self.set_up_patch('raptiformica.actions.mesh.gethostname')
        self.gethostname.return_value = 'myhostname'
        self.mapping = {
            "raptiformica/meshnet/cjdns/password": "a_secret",
            "raptiformica/meshnet/consul/password": "a_different_secret",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_ipv6_address": "some_ipv6_address",
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_pubkey.k/cjdns_public_key": "a_pubkey.k",
            "raptiformica/meshnet/neighbours/a_pubkey.k/host": "192.168.178.23",
            "raptiformica/meshnet/neighbours/a_pubkey.k/ssh_port": "2200",
            "raptiformica/meshnet/neighbours/a_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf2",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_ipv6_address": "some_other_ipv6_address",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_port": 4863,
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/cjdns_public_key": "a_different_pubkey.k",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/host": "192.168.178.24",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/ssh_port": "2201",
            "raptiformica/meshnet/neighbours/a_different_pubkey.k/uuid": "eb442c6170694b12b277c9e88d714cf1",
        }
        self.get_config = self.set_up_patch('raptiformica.actions.mesh.get_config_mapping')
        self.get_config.return_value = self.mapping
        self.cjdroute_config = {
            'ipv6': 'the_ipv6_address',
        }
        self.load_json = self.set_up_patch('raptiformica.actions.mesh.load_json')
        self.load_json.return_value = self.cjdroute_config
        self.ensure_directory = self.set_up_patch('raptiformica.actions.mesh.ensure_directory')
        self.write_json = self.set_up_patch('raptiformica.actions.mesh.write_json')

    def test_configure_consul_conf_logs_configuring_consul_config_message(self):
        configure_consul_conf()

        self.assertTrue(self.log.info.called)

    def test_configure_consul_conf_loads_cjdroute_config(self):
        configure_consul_conf()

        self.load_json.assert_called_once_with(CJDROUTE_CONF_PATH)

    def test_configure_consul_conf_ensures_consul_settings_directories_exist(self):
        configure_consul_conf()

        expected_calls = [
            call('/etc/consul.d'),
            call('/etc/opt.consul')
        ]
        self.assertTrue(expected_calls, self.ensure_directory.mock_calls)

    def test_configure_consul_conf_writes_generated_consul_conf_to_disk(self):
        configure_consul_conf()

        expected_config = {
            'bootstrap_expect': 3,
            'data_dir': '/opt/consul',
            'datacenter': 'raptiformica',
            'log_level': 'INFO',
            'node_name': 'myhostname',
            # deterministic node ID derived from the IPv6 address
            'node_id': '1d08bba2-6d04-b253-d647-a7fd84e2002a',
            'server': True,
            'bind_addr': '::',
            'advertise_addr': 'the_ipv6_address',
            'encrypt': 'a_different_secret',
            'disable_remote_exec': True,
            'enable_script_checks': True,
            'performance': {
                # Low sensitivity settings. Machines leave
                # and join the cluster fast and often.
                'raft_multiplier': 10
            },
            'dns_config': {
                'allow_stale': True,
                "recursor_timeout": '1s'
            },
            "leave_on_terminate": True,
            "skip_leave_on_interrupt": False,
            "disable_update_check": True,
            "reconnect_timeout": "8h",  # The value must be >= 8 hours.
            "reconnect_timeout_wan": "8h",
            "translate_wan_addrs": False,
            "rejoin_after_leave": True,
            'watches': [
                {
                    'type': 'service',
                    'service': 'consul',
                    'handler': "bash -c \""
                               "cd '/usr/etc/raptiformica'; "
                               "export PYTHONPATH=.; "
                               "./bin/raptiformica_hook.py cluster_change "
                               "--verbose"
                               "\""
                },
                {
                    'type': 'event',
                    'name': 'notify_cluster_change',
                    'handler': "bash -c \""
                               "cd '/usr/etc/raptiformica'; "
                               "export PYTHONPATH=.; "
                               "./bin/raptiformica_hook.py cluster_change "
                               "--verbose"
                               "\""
                },
            ]
        }
        self.write_json.assert_called_once_with(
            expected_config,
            CONSUL_CONF_PATH
        )
