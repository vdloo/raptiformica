from multiprocessing.pool import ThreadPool
from os import environ
from unittest import SkipTest

from tests.testcase import IntegrationTestCase, run_raptiformica_command


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
    def spawn_docker_instances(self):
        spawn_command = "spawn --server-type headless --compute-type docker"
        for _ in range(self.amount_of_instances):
            run_raptiformica_command(self.temp_cache_dir, spawn_command)

    def reslave_last_docker_instance(self):
        docker_instances = self.list_relevant_docker_instances()
        docker_ip = self.get_docker_ip(docker_instances[-1])
        self.slave_instance(docker_ip)

    def skip_if_env_override(self):
        if environ.get('NO_NO_CONCURRENT'):
            raise SkipTest

    def setUp(self):
        self.skip_if_env_override()
        super(TestSimpleCluster, self).setUp()
        self.amount_of_instances = 3
        self.spawn_docker_instances()

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


class TestSimpleConcurrentCluster(TestSimpleCluster):
    """
    Same as the SimpleCluster case but all instances boot at the same time
    instead of one after the other.
    """
    workers = 3

    def skip_if_env_override(self):
        if environ.get('NO_FULL_CONCURRENT'):
            raise SkipTest

    def spawn_docker_instances(self):
        spawn_command = "spawn --server-type headless --compute-type docker"
        pool = ThreadPool(self.workers)
        for _ in range(self.amount_of_instances):
            pool.apply_async(
                run_raptiformica_command,
                args=(self.temp_cache_dir, spawn_command)
            )


class TestSimpleSemiConcurrentCluster(TestSimpleConcurrentCluster):
    """
    Same as the SimpleCluster case but all two of the three instances boot
    at the same time instead of one after the other.
    """
    workers = 2

    def skip_if_env_override(self):
        if environ.get('NO_SEMI_CONCURRENT'):
            raise SkipTest
