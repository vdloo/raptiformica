from tests.testcase import IntegrationTestCase


class TestLinkedCluster(IntegrationTestCase):
    """
    Test a linked cluster of three Docker instances. This test case simulates a
    situation where instance A can reach B using an address that only has meaning
    to A. The same goes for B to C. This means that the address that A uses to connect
    to B can not be used by C to connect to B. The address used by B to connect to C can
    not be used by A to connect to C. A is unreachable fo C and the other way around.

    The only path is then:

    .===.   .===.   .===.
    | A |->-| B |->-| C |
    '==='   '==='   '==='

    This scenario tests whether starting from A, slaving B will create a reverse
    route using CJDNS from B to A and that slaving C from B will create another
    reverse route. C should then be able to connect to A using the two tunnels
    and vice versa. This simulates a firewalled scenario where a host can connect
    to another host which then can also connect to yet another host, one that is
    not accessible by the first host.
    """
    def spawn_docker_instances(self):
        self.run_raptiformica_command("spawn --no-assimilate --server-type headless --compute-type docker")

    def setUp(self):
        super(TestLinkedCluster, self).setUp()
        self.amount_of_instances = 3

        # Spawn 3 un-assimilated Docker instances
        for _ in range(self.amount_of_instances):
            self.spawn_docker_instances()

        # List the spawned instances and their IPs
        docker_instances = self.list_docker_instances()
        docker_ips = list(map(self.get_docker_ip, docker_instances))

        # Ensure the requirements are installed
        self.ensure_raptiformica_requirements(docker_instances)

        # Make the first instance DNAT 1.2.3.4 to 172.17.0.4 etc
        first_instance_firewalled_ips = list(
            self.pretend_behind_firewall(docker_instances[0], docker_ips, subnet="1.2.3.{}")
        )

        # Make the second instance DNAT 2.2.3.4 to 172.17.0.4 etc
        second_instance_firewalled_ips = list(
            self.pretend_behind_firewall(docker_instances[1], docker_ips, subnet="2.3.4.{}")
        )

        # Assimilate one of the instances from the client (which is not in the cluster)
        # so we can later run raptiformica members without having to log in explicitly.
        self.run_raptiformica_command(
            "slave {} --server-type headless --verbose".format(docker_ips[0])
        )

        # Install the uploaded raptiformica systemwide on the first two instances
        # so we can run 'raptiformica' without having to specify the PYTHONPATH and
        # project path.
        for i in range(2):
            self.install_raptiformica_in_docker(docker_instances[i])
            # Make sure the instance has no lingering data
            self.clear_mutable_config(docker_instances[i])

        # Perform the raptiformica command on the first instance
        # A will assimilate A, then A will assimilate B.
        self.slave_from_firewalled_environment(docker_ips[0], docker_ips[:1])
        self.slave_from_firewalled_environment(
            docker_ips[0], first_instance_firewalled_ips[1:2]
        )

        # Perform the raptiformica command on the second instance
        # B will assimilate C
        self.slave_from_firewalled_environment(
            docker_ips[1], second_instance_firewalled_ips[2:]
        )

    def test_linked_cluster_establishes_mesh_correctly(self):
        self.check_consul_consensus_was_established(expected_peers=self.amount_of_instances)
        self.check_all_registered_peers_can_be_pinged_from_any_instance()
