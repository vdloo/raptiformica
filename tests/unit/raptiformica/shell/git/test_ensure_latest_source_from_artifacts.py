from mock import call, Mock

from raptiformica.settings import conf
from raptiformica.shell.git import ensure_latest_source_from_artifacts
from tests.testcase import TestCase


class TestEnsureLatestSourceFromArtifacts(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.ensure_directory = self.set_up_patch(
            'raptiformica.shell.git.ensure_directory'
        )
        self.ensure_latest_source = self.set_up_patch(
            'raptiformica.shell.git.ensure_latest_source'
        )
        self.conf = self.set_up_patch(
            'raptiformica.shell.git.conf'
        )
        self.conf.return_value = Mock(
            ABS_CACHE_DIR='/home/someuser/.raptiformica.temp.custom',
            CACHE_DIR='.raptiformica.temp.custom',
            INSTALL_DIR='/usr/etc/'
        )

    def test_ensure_latest_source_from_artifacts_ensures_artifacts_directory(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", port=22
        )

        self.ensure_directory.assert_called_once_with(
            '/home/someuser/.raptiformica.temp.custom/artifacts/repositories'
        )

    def test_ensure_latest_source_from_artifacts_ensures_artifacts_dir_in_default_cache_on_remote_hosts(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        self.ensure_directory.assert_called_once_with(
            '.raptiformica.d/artifacts/repositories'
        )

    def test_ensure_latest_source_from_artifacts_ensures_cached_source_to_install_dir(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", port=22
        )

        expected_calls = (
            call(
                "https://github.com/vdloo/puppetfiles",
                "puppetfiles", host=None, port=22,
                destination='/home/someuser/.raptiformica.temp.custom/artifacts/repositories'
            ),
            call(
                "file:///root/.raptiformica.d/artifacts/repositories/puppetfiles",
                "puppetfiles", host=None, port=22,
                destination=conf().INSTALL_DIR
            )
        )
        self.assertCountEqual(self.ensure_latest_source.mock_calls, expected_calls)

    def test_ensure_latest_source_from_artifacts_ensures_cached_source_to_install_dir_on_remote_hosts(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        expected_calls = (
            call(
                "https://github.com/vdloo/puppetfiles",
                "puppetfiles", host='1.2.3.4', port=22,
                destination='.raptiformica.d/artifacts/repositories'
            ),
            call(
                "file:///root/.raptiformica.d/artifacts/repositories/puppetfiles",
                "puppetfiles", host='1.2.3.4', port=22,
                destination=conf().INSTALL_DIR
            )
        )
        self.assertCountEqual(self.ensure_latest_source.mock_calls, expected_calls)

    def test_ensure_latest_source_from_artifacts_ensures_cached_source_to_specified_dir(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", port=22,
            destination='/tmp/some/other/directory'
        )

        expected_calls = (
            call(
                "https://github.com/vdloo/puppetfiles",
                "puppetfiles", host=None, port=22,
                destination='/home/someuser/.raptiformica.temp.custom/artifacts/repositories'
            ),
            call(
                "file:///root/.raptiformica.d/artifacts/repositories/puppetfiles",
                "puppetfiles", host=None, port=22,
                destination='/tmp/some/other/directory'
            )
        )
        self.assertCountEqual(self.ensure_latest_source.mock_calls, expected_calls)

    def test_ensure_latest_source_from_artifacts_ensures_only_cache_if_only_cache(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", port=22,
            only_cache=True
        )

        self.ensure_latest_source.assert_called_once_with(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host=None, port=22,
            destination='/home/someuser/.raptiformica.temp.custom/artifacts/repositories'
        )

    def test_ensure_latest_source_from_artifacts_ensures_cached_source_to_specified_dir_on_remote_hosts(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
            destination='/tmp/some/other/directory'
        )

        expected_calls = (
            call(
                "https://github.com/vdloo/puppetfiles",
                "puppetfiles", host='1.2.3.4', port=22,
                destination='.raptiformica.d/artifacts/repositories'
            ),
            call(
                "file:///root/.raptiformica.d/artifacts/repositories/puppetfiles",
                "puppetfiles", host='1.2.3.4', port=22,
                destination='/tmp/some/other/directory'
            )
        )
        self.assertCountEqual(self.ensure_latest_source.mock_calls, expected_calls)

    def test_ensure_latest_source_from_artifacts_ensures_only_cache_if_only_cache_on_remote_hosts(self):
        ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
            only_cache=True
        )

        self.ensure_latest_source.assert_called_once_with(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
            destination='.raptiformica.d/artifacts/repositories'
        )

    def test_ensure_latest_source_from_artifacts_returns_cached_ensure_result(self):
        expected_result = Mock()
        self.ensure_latest_source.side_effect = [Mock(), expected_result]

        ret = ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22
        )

        self.assertEqual(ret, expected_result)

    def test_ensure_latest_source_from_artifacts_returns_cache_creation_ensure_result_if_only_cache(self):
        expected_result = Mock()
        # Only one ensure_latest_source call was performed
        self.ensure_latest_source.side_effect = [expected_result]

        ret = ensure_latest_source_from_artifacts(
            "https://github.com/vdloo/puppetfiles",
            "puppetfiles", host='1.2.3.4', port=22,
            only_cache=True
        )

        self.assertEqual(ret, expected_result)
