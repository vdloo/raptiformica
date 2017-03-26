import unittest
from functools import partial
from os.path import expanduser
from os.path import join
from uuid import uuid4

from mock import patch, Mock
from shutil import rmtree

from os import makedirs

from raptiformica.settings import conf
from raptiformica.settings.load import upload_config_mapping
from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory


class TestCase(unittest.TestCase):
    def set_up_patch(self, patch_target, mock_target=None, **kwargs):
        patcher = patch(patch_target, mock_target or Mock(**kwargs))
        self.addCleanup(patcher.stop)
        return patcher.start()


class IntegrationTestCase(TestCase):
    def run_raptiformica_command(self, parameters, buffered=False):
        raptiformica_command = "{}/bin/raptiformica {} --cache-dir {} " \
                               "".format(conf().PROJECT_DIR.rstrip('/'),
                                           parameters, self.temp_cache_dir)
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
        raptiformica_command = "`{}/bin/raptiformica ssh --info-only " \
                               "--cache-dir {}` {}" \
                               "".format(conf().PROJECT_DIR.rstrip('/'),
                                         self.temp_cache_dir,
                                         command_as_string)
        _, standard_out, standard_error = run_command_print_ready(
            raptiformica_command,
            buffered=buffered, shell=True
        )
        return standard_out

    def kill_all_dockers(self):
        # todo: only kill the dockers relevant to each test process
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
        rmtree(conf().ABS_CACHE_DIR, ignore_errors=True)

    def setUp(self):
        self.kill_all_dockers()
        self.clean_all_docker_images()
        self.clean_up_cache_dir()
        print("Cleaned up any lingering state\n\n")

        self.temp_cache_dir = '.raptiformica.test.{}'.format(uuid4().hex)
        conf().set_cache_dir(self.temp_cache_dir)
        self.abs_temp_cache_dir = join(expanduser("~"), self.temp_cache_dir)
        makedirs(self.abs_temp_cache_dir)

    def check_consul_consensus_was_established(self, expected_peers=None):
        consul_members_output = self.run_raptiformica_command("members", buffered=True)
        alive_agents = consul_members_output.count("alive")
        if expected_peers is None:
            self.assertGreaterEqual(
                alive_agents, 3,
                msg="Did not find enough ({} of at least 3) alive agents. "
                    "consul members output: {}".format(alive_agents,
                                                       consul_members_output)
            )
        else:
            self.assertEqual(
                alive_agents, expected_peers,
                msg="Did not find enough ({} of the {}) alive agents. "
                    "consul members output: {}".format(alive_agents,
                                                       expected_peers,
                                                       consul_members_output)
            )

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

    def docker_instance_is_relevant(self, instance_id):
        """
        Check if a docker instance is relevant oo this
        testcase
        :param str instance_id: The docker ID to check
        :return bool relevant: True if relevant, False if not
        """
        # If the cjdns password from the in use temporary cache dir matches the secret
        # in the guest, that means the docker belongs to this test case
        check_relevant_command = 'sudo docker exec {} cat /root/.raptiformica.d/mutable_config.json | ' \
                                 'grep "$(grep raptiformica/meshnet/cjdns/password ' \
                                 '{}/mutable_config.json)"' \
                                 ''.format(instance_id, self.abs_temp_cache_dir)
        exit_code, _, __ = run_command_print_ready(
            check_relevant_command,
            buffered=False, shell=True
        )
        return exit_code == 0

    def list_relevant_docker_instances(self):
        """
        Find the running docker instances on the host that belong
        to this running testcase
        :return list[str, ..]: List of docker IDs
        """
        all_docker_instances = self.list_docker_instances()
        return list(filter(
            self.docker_instance_is_relevant,
            all_docker_instances
        ))

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

        # Try to connect to the remote consul instead of using the local cache
        conf().set_forwarded_remote_consul_once(set_to=False)

        upload_config_mapping({'test/some/key/in/some/path': expected_value})
        ret = self.run_instance_command(
            '"consul kv get -recurse | grep test"', buffered=True
        )
        self.assertIn(expected_value, ret)

    def ensure_package_installed(self, docker_instance, package):
        install_package_command = "sudo docker exec {} apt-get install " \
                                  "{} -yy".format(docker_instance, package)
        run_command_print_ready(
            install_package_command, buffered=False, shell=True,
            failure_callback=raise_failure_factory(
                "Failed to install {} on the testhost. Could not set up "
                "the scenario for TestLinkedCluster :(".format(package)
            )
        )

    def ensure_raptiformica_installed(self, docker_instance):
        install_raptiformica_command = "sudo docker exec {} bash -c '" \
                                       "cd /usr/etc/raptiformica; " \
                                       "make install'" \
                                       "".format(docker_instance)
        run_command_print_ready(
            install_raptiformica_command, buffered=False, shell=True,
            failure_callback=raise_failure_factory(
                "Failed to install raptiformica on the testhost. "
                "Could not set up the scenario for TestTreeCluster :("
            )
        )

    def preroute_docker_ip(self, docker_instance, docker_ip, subnet='1.2.3.{}'):
        last_octet = docker_ip.split('.')[-1]
        natted_ip = subnet.format(last_octet)
        preroute_ip_commmand = "sudo docker exec {} " \
                               "iptables -t nat -A OUTPUT -p all " \
                               "-d {} -j DNAT " \
                               "--to-destination {}" \
                               "".format(docker_instance,
                                         natted_ip, docker_ip)
        run_command_print_ready(
            preroute_ip_commmand, buffered=False, shell=True,
            failure_callback=raise_failure_factory(
                "Failed to install prerouting rule for {} on the testhost. "
                "Could not set up the scenario for TestTreeCluster :("
                "".format(docker_ip)
            )
        )
        return natted_ip

    def pretend_behind_firewall(self, docker_instance, docker_ips, subnet='1.2.3.{}'):
        """
        Add iptables rules to the instance so that the docker IPs can be
        reached through an aliased IP. This way the system will propagate
        those IPs to the other instances but they won't be able to reach
        the addresses because they will route to nothing because those
        other instances don't have the pre-routing rules.
        :param str docker_instance: ID of the Docker instance to perform
        the aliased routing on
        :param list docker_ips: List of IPs to re-route
        param str subnet: The subnet formatter to route behind
        :return iter NATted_ips: The re-routed IPs
        """
        self.ensure_package_installed(docker_instance, 'iptables')
        return map(
            partial(self.preroute_docker_ip, docker_instance, subnet=subnet),
            docker_ips
        )

    def ensure_raptiformica_requirements(self, docker_instances):
        """
        Install the requirements for raptiformica
        :param list [str instance, ..] docker_instances: List of docker instances
        :return None:
        """
        for docker_instance in docker_instances:
            for package in ('make', 'sudo', 'iputils-ping'):
                self.ensure_package_installed(docker_instance, package)

    def clear_mutable_config(self, docker_instance):
        """
        Remove the mutable config in a docker
        :param str docker_instance: ID of the Docker instance to clear the
        mutable config on
        :return None:
        """
        clear_mutable_config = "sudo docker exec {} " \
                               "rm -f /root/.raptiformica.d/mutable_config.json" \
                               "".format(docker_instance)
        run_command_print_ready(
            clear_mutable_config, buffered=False, shell=True,
            failure_callback=raise_failure_factory(
                "Failed to clear the cached config on the testhost. "
                "Could not set up the scenario for TestTreeCluster :("
            )
        )

    def install_raptiformica_in_docker(self, docker_instance):
        """
        Install raptiformica system wide in the instance
        :param str docker_instance: ID of the Docker instance to install
        raptiformica system wide in
        :return None:
        """
        self.ensure_raptiformica_installed(docker_instance)

    def slave_from_firewalled_environment(self, docker_ip, NATted_ips):
        """
        Slave the Docker instances from behind the firewall.
        :param str docker_ip: IP of the Docker instance to perform
        the raptiformica commands on
        :param list NATted_ips: list of the NATted IPs to slave
        :return None:
        """
        for NATted_ip in NATted_ips:
            slave_instance_command = "ssh -oStrictHostKeyChecking=no " \
                                     "-oUserKnownHostsFile=/dev/null " \
                                     "-A root@{} raptiformica " \
                                     "slave {} --verbose" \
                                     "".format(docker_ip, NATted_ip)
            run_command_print_ready(
                slave_instance_command, buffered=False, shell=True,
                failure_callback=raise_failure_factory(
                    "Failed to slave the NATted ip {}. Could not set up "
                    "the scenario for TestTreeCluster :(".format(NATted_ip)
                )
            )

    def slave_instance(self, ip_address):
        self.run_raptiformica_command(
            "slave {}".format(ip_address)
        )

    def tearDown(self):
        print("Finished running this test case, cleaning up the resources\n\n")
        self.kill_all_dockers()
        self.clean_all_docker_images()
        self.clean_up_cache_dir()
        rmtree(self.abs_temp_cache_dir, ignore_errors=True)
