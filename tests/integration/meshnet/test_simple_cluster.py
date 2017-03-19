from tests.testcase import IntegrationTestCase


class TestSimpleCluster(IntegrationTestCase):
    """
    Test a simple cluster of three Docker instances in the same subnet.
    All instances can reach each other directly over an IPv4 interface.

    All instances can reach all instances

    .===.   .===.   .===.
    | A |<->| B |<->| C |
    '=|='   '==='   '=|='
      '======<=>======'

    This simulates a subnet in a data-center for example.
    """
    def spawn_docker_instance(self):
        self.run_raptiformica_command(
            "spawn --server-type headless --compute-type docker"
        )

    def reslave_last_docker_instance(self):
        docker_instances = self.list_docker_instances()
        docker_ip = self.get_docker_ip(docker_instances[-1])
        self.slave_instance(docker_ip)

    def setUp(self):
        super(TestSimpleCluster, self).setUp()
        self.amount_of_instances = 3
        for _ in range(self.amount_of_instances):
            self.spawn_docker_instance()

    def verify_cluster_is_operational(self):
        self.check_consul_consensus_was_established(
            expected_peers=self.amount_of_instances
        )
        self.check_all_registered_peers_can_be_pinged_from_any_instance()
        self.check_data_can_be_stored_in_the_distributed_kv_store()

    def test_simple_cluster_establishes_mesh_correctly(self):
        # Test if the cluster is operational after initial creation
        self.verify_cluster_is_operational()

        # Test if the cluster is still operational
        # after re-slaving one of the machines
        self.reslave_last_docker_instance()
        self.verify_cluster_is_operational()
