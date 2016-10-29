from raptiformica.actions.destroy import destroy_cluster
from tests.testcase import TestCase


class TestDestroyCluster(TestCase):
    def setUp(self):
        self.shutdown_all_instances = self.set_up_patch(
            'raptiformica.actions.destroy.shutdown_all_instances'
        )
        self.prune_local_machines = self.set_up_patch(
            'raptiformica.actions.destroy.prune_local_machines'
        )
        self.purge_config = self.set_up_patch(
            'raptiformica.actions.destroy.purge_config'
        )

    def test_destroy_cluster_shuts_down_all_instances(self):
        destroy_cluster()

        self.shutdown_all_instances.assert_called_once_with()

    def test_destroy_cluster_force_prunes_local_machines(self):
        destroy_cluster()

        self.prune_local_machines.assert_called_once_with(force=True)

    def test_destroy_cluster_purges_config(self):
        destroy_cluster()

        self.purge_config.assert_called_once_with(
            purge_artifacts=False,
            purge_modules=False
        )

    def test_destroy_cluster_purges_config_with_artifacts_if_specified(self):
        destroy_cluster(purge_artifacts=True)

        self.purge_config.assert_called_once_with(
                purge_artifacts=True,
                purge_modules=False
        )

    def test_destroy_cluster_purges_config_with_modules_if_specified(self):
        destroy_cluster(purge_modules=True)

        self.purge_config.assert_called_once_with(
                purge_artifacts=False,
                purge_modules=True
        )
