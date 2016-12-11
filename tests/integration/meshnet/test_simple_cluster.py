from tests.testcase import IntegrationTestCase


class TestSimpleCluster(IntegrationTestCase):
    def spawn_docker_instance(self):
        self.run_raptiformica_command("spawn --server-type headless --compute-type docker")

    def setUp(self):
        super(TestSimpleCluster, self).setUp()
        self.amount_of_instances = 3
        for _ in range(self.amount_of_instances):
            self.spawn_docker_instance()

    def test_simple_cluster_establishes_mesh_correctly(self):
        self.check_consul_consensus_was_established(
            expected_peers=self.amount_of_instances
        )
        self.check_all_registered_peers_can_be_pinged_from_any_instance()
        self.check_data_can_be_stored_in_the_distributed_kv_store()
