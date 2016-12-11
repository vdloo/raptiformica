from functools import partial

from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory
from tests.testcase import IntegrationTestCase


class TestTreeCluster(IntegrationTestCase):
    """
    Test a tree cluster of three Docker instances. This test case simulates a
    situation where instance A can reach B using an address that only has meaning
    to A. The same goes for A to C. This means that the address that A uses to connect
    to B can not be used by C to connect to B. The address used by A to connect to C can
    not be used by B to connect to C. A is unreachable for both B and C.

    The only path is then:

    .===.   .===.   .===.
    | A |->-| B |   | C |
    '=|='   '==='   '-|-'
      '=======>======='

    This scenario tests whether starting from A, slaving B will create a reverse
    route using CJDNS from B to A and that slaving C from A will create another
    reverse route. C should then be able to connect to B using the two tunnels
    and vice versa. This simulates a NAT-like scenario where a firewalled host
    can connect two public hosts with each other through the host behind the
    firewall. The two public hosts (B and C) do not connect directly.
    """
    def spawn_docker_instances(self):
        self.run_raptiformica_command("spawn --no-assimilate --server-type headless --compute-type docker")

    def ensure_iptables_installed(self, docker_instance):
        install_iptables_command = "sudo docker exec {} apt-get install " \
                                   "iptables -yy".format(docker_instance)
        run_command_print_ready(
            install_iptables_command, buffered=False, shell=True,
            failure_callback=raise_failure_factory(
                "Failed to install iptables on the testhost. Could not set up "
                "the scenario for TestTreeCluster :("
            )
        )

    def ensure_make_installed(self, docker_instance):
        install_make_command = "sudo docker exec {} apt-get install " \
                               "make -yy".format(docker_instance)
        run_command_print_ready(
            install_make_command, buffered=False, shell=True,
            failure_callback=raise_failure_factory(
                "Failed to install make on the testhost. Could not set up "
                "the scenario for TestTreeCluster :("
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

    def preroute_docker_ip(self, docker_instance, docker_ip):
        last_octet = docker_ip.split('.')[-1]
        natted_ip = "1.2.3.{}".format(last_octet)
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

    def pretend_behind_firewall(self, docker_instance, docker_ips):
        """
        Add iptables rules to the instance so that the docker IPs can be
        reached through an aliased IP. This way the system will propagate
        those IPs to the other instances but they won't be able to reach
        the addresses because they will route to nothing because those
        other instances don't have the pre-routing rules.
        :param str docker_instance: ID of the Docker instance to perform
        the aliased routing on
        :param list docker_ips: List of IPs to re-route
        :return iter NATted_ips: The re-routed IPs
        """
        self.ensure_iptables_installed(docker_instance)
        return map(partial(self.preroute_docker_ip, docker_instance), docker_ips)

    def install_raptiformica_in_docker(self, docker_instance):
        """
        Install raptiformica system wide in the instance
        :param str docker_instance: ID of the Docker instance to install
        raptiformica system wide in
        :return None:
        """
        self.ensure_make_installed(docker_instance)
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

    def setUp(self):
        super(TestTreeCluster, self).setUp()
        self.amount_of_instances = 3

        # Spawn 3 un-assimilated Docker instances
        for _ in range(self.amount_of_instances):
            self.spawn_docker_instances()

        # List the spawned instances and their IPs
        docker_instances = self.list_docker_instances()
        docker_ips = list(map(self.get_docker_ip, docker_instances))

        # Make the first instance DNAT 1.2.3.4 to 172.17.0.4 etc
        NATted_ips = list(self.pretend_behind_firewall(docker_instances[0], docker_ips))

        # Assimilate one of the instances from the client (which is not in the cluster)
        # so we can later run raptiformica members without having to log in explicitly.
        self.run_raptiformica_command(
            "slave {} --server-type headless".format(docker_ips[0])
        )

        # Install the uploaded raptiformica systemwide so we can run 'raptiformica'
        # without having to specify the PYTHONPATH and project path.
        self.install_raptiformica_in_docker(docker_instances[0])

        # Perform the raptiformica commands on the first instance
        # A will assimilate A, then A will assimilate B and then C.
        self.slave_from_firewalled_environment(docker_ips[0], NATted_ips)

    def test_simple_cluster_establishes_mesh_correctly(self):
        self.check_consul_consensus_was_established(
            expected_peers=self.amount_of_instances
        )
        self.check_all_registered_peers_can_be_pinged_from_any_instance()
        self.check_data_can_be_stored_in_the_distributed_kv_store()
