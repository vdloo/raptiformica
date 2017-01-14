from raptiformica.settings import conf
from raptiformica.shell.rsync import download_artifacts
from tests.testcase import TestCase


class TestDownloadArtifacts(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.shell.rsync.log')
        self.download = self.set_up_patch('raptiformica.shell.rsync.download')
        self.download.return_value = 0

    def test_download_artifacts_logs_downloading_artifacts_message(self):
        download_artifacts('1.2.3.4', port=2222)

        self.assertTrue(self.log.info.called)

    def test_download_artifacts_downloads_artifacts_from_remote_host(self):
        download_artifacts('1.2.3.4', port=2222)

        self.download.assert_called_once_with(
            '.raptiformica.d/artifacts',
            conf().ABS_CACHE_DIR,
            host='1.2.3.4',
            port=2222
        )

    def test_download_artifacts_returns_true_if_success(self):
        ret = download_artifacts('1.2.3.4', port=2222)

        self.assertTrue(ret)

    def test_download_artifacts_returns_false_if_failure(self):
        self.download.return_value = 1

        ret = download_artifacts('1.2.3.4', port=2222)

        self.assertFalse(ret)
