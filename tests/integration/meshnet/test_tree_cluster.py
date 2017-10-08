from multiprocessing.pool import ThreadPool
from os import environ
from time import sleep
from unittest import SkipTest

from raptiformica.settings.meshnet import ensure_shared_secret
from tests.testcase import IntegrationTestCase, run_raptiformica_command


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
    '=|='   '==='   '=|='
      '=======>======='

    This scenario tests whether starting from A, slaving B will create a reverse
    route using CJDNS from B to A and that slaving C from A will create another
    reverse route. C should then be able to connect to B using the two tunnels
    and vice versa. This simulates a NAT-like scenario where a firewalled host
    can connect two public hosts with each other through the host behind the
    firewall. The two public hosts (B and C) do not connect directly.
    """
    def spawn_docker_instances(self):
        spawn_command = "spawn --no-assimilate " \
                        "--server-type headless " \
                        "--compute-type docker"
        for _ in range(self.amount_of_instances):
            run_raptiformica_command(self.temp_cache_dir, spawn_command)

    def skip_if_env_override(self):
        if environ.get('NO_NO_CONCURRENT'):
            raise SkipTest

    def setUp(self):
        self.skip_if_env_override()
        super(TestTreeCluster, self).setUp()
        self.amount_of_instances = 3

        # Spawn 3 un-assimilated Docker instances
        self.spawn_docker_instances()

        # List the spawned instances and their IPs
        docker_instances = self.list_relevant_docker_instances(expected=self.amount_of_instances)
        docker_ips = list(map(self.get_docker_ip, docker_instances))

        # Ensure the requirements are installed
        self.ensure_raptiformica_requirements(docker_instances)

        # Make the first instance DNAT 1.2.3.4 to 172.17.0.4 etc
        NATted_ips = list(self.pretend_behind_firewall(docker_instances[0], docker_ips))

        # Assimilate one of the instances from the client (which is not in the cluster)
        # so we can later run raptiformica members without having to log in explicitly.
        run_raptiformica_command(
            self.temp_cache_dir,
            "slave {} --server-type headless --verbose".format(docker_ips[0])
        )

        # Install the uploaded raptiformica systemwide so we can run 'raptiformica'
        # without having to specify the PYTHONPATH and project path.
        self.install_raptiformica_in_docker(docker_instances[0])

        # Make sure the instance has no lingering data
        self.clear_mutable_config(docker_instances[0])

        # Perform the raptiformica commands on the first instance
        # A will assimilate A, then A will assimilate B and then C.
        self.slave_from_firewalled_environment(docker_ips[0], docker_ips[:1])
        self.slave_from_firewalled_environment(docker_ips[0], NATted_ips[1:])

    def test_tree_cluster_establishes_mesh_correctly(self):
        self.check_consul_consensus_was_established(expected_peers=self.amount_of_instances)
        self.check_all_registered_peers_can_be_pinged_from_any_instance()


class TestTreeConcurrentCluster(TestTreeCluster):
    """
    Same as the TreeCluster case but all instances boot at the same time
    instead of one after the other.
    """
    workers = 3

    def skip_if_env_override(self):
        if environ.get('NO_FULL_CONCURRENT'):
            raise SkipTest

    def spawn_docker_instances(self):
        # Must create shared secret beforehand otherwise the
        # testcase does not know which instances are relevant
        ensure_shared_secret('cjdns')

        spawn_command = "spawn --no-assimilate " \
                        "--server-type headless " \
                        "--compute-type docker"
        pool = ThreadPool(self.workers)
        for _ in range(self.amount_of_instances):
            pool.apply_async(
                run_raptiformica_command,
                args=(self.temp_cache_dir, spawn_command)
            )
            sleep(20)
        pool.close()
        pool.join()
