from mock import ANY, call

from raptiformica.actions.spawn import cache_repos
from raptiformica.shell.cjdns import CJDNS_REPOSITORY
from raptiformica.shell.consul import CONSUL_KV_REPOSITORY
from tests.testcase import TestCase


class TestCacheRepos(TestCase):
    def setUp(self):
        self.log = self.set_up_patch(
            'raptiformica.actions.spawn.log'
        )
        self.ensure_source_on_machine = self.set_up_patch(
            'raptiformica.actions.spawn.ensure_source_on_machine'
        )
        self.ensure_latest_source_from_artifacts = self.set_up_patch(
            'raptiformica.actions.spawn.ensure_latest_source_from_artifacts'
        )

    def test_cache_repos_logs_info_message(self):
        cache_repos()

        self.log.info.assert_called_once_with(ANY)

    def test_cache_repos_ensures_source_on_machine(self):
        cache_repos()

        self.ensure_source_on_machine.assert_called_once_with(
            server_type=None, only_cache=True
        )

    def test_cache_repos_ensures_source_on_machine_using_specified_server_type(self):
        cache_repos(server_type='workstation')

        self.ensure_source_on_machine.assert_called_once_with(
            server_type='workstation', only_cache=True
        )

    def test_cache_repos_ensures_latest_sources_from_artifacts_for_non_provisioning_source(self):
        cache_repos()

        # These sources are not in the provisioning configs (modules)
        # but are required for the core code
        expected_calls = (
            call(
                CJDNS_REPOSITORY, "cjdns", only_cache=True
            ),
            call(
                CONSUL_KV_REPOSITORY, "consul-kv", only_cache=True
            ),
        )
        self.assertCountEqual(
            self.ensure_latest_source_from_artifacts.mock_calls, expected_calls
        )
