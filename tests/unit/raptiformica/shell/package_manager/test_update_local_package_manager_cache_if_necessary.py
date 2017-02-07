from raptiformica.settings import conf
from raptiformica.shell.package_manager import update_local_package_manager_cache_if_necessary
from tests.testcase import TestCase


class TestUpdateLocalPackageManagerCacheIfNecessary(TestCase):
    def setUp(self):
        self.file_age_in_seconds = self.set_up_patch(
            'raptiformica.shell.package_manager.file_age_in_seconds'
        )
        self.file_age_in_seconds.return_value = conf().PACKAGE_MANAGER_CACHE_OUTDATED + 1
        self.isfile = self.set_up_patch(
            'raptiformica.shell.package_manager.isfile'
        )
        self.isfile.return_value = True
        self.update_package_manager_cache = self.set_up_patch(
            'raptiformica.shell.package_manager.update_package_manager_cache'
        )
        self.path = self.set_up_patch(
            'raptiformica.shell.package_manager.Path'
        )

    def test_update_local_package_manager_cache_if_necessary_checks_if_updated_file_exists(self):
        update_local_package_manager_cache_if_necessary()

        self.isfile.assert_called_once_with(
            conf().PACKAGE_MANGER_UPDATED
        )

    def test_update_local_package_manager_cache_does_not_check_updated_file_age_if_no_file(self):
        self.isfile.return_value = False

        update_local_package_manager_cache_if_necessary()

        self.assertFalse(self.file_age_in_seconds.called)

    def test_update_local_package_manager_cache_checks_file_age_in_seconds_if_updated_file_exists(self):
        update_local_package_manager_cache_if_necessary()

        self.file_age_in_seconds.assert_called_once_with(
            conf().PACKAGE_MANGER_UPDATED
        )

    def test_update_local_package_manager_cache_updates_package_manager_cache_if_file_too_old(self):
        update_local_package_manager_cache_if_necessary()

        self.update_package_manager_cache.assert_called_once_with()

    def test_update_local_package_manager_cache_touches_the_updated_file_if_file_too_old(self):
        update_local_package_manager_cache_if_necessary()

        self.path.assert_called_once_with(conf().PACKAGE_MANGER_UPDATED)
        self.path.return_value.touch.assert_called_once_with()

    def test_update_local_package_manager_cache_updates_package_manager_cache_if_no_file_yet(self):
        self.isfile.return_value = False

        update_local_package_manager_cache_if_necessary()

        self.update_package_manager_cache.assert_called_once_with()

    def test_update_local_package_manager_cache_touches_the_updated_file_if_no_file_yet(self):
        self.isfile.return_value = False

        update_local_package_manager_cache_if_necessary()

        self.path.assert_called_once_with(conf().PACKAGE_MANGER_UPDATED)
        self.path.return_value.touch.assert_called_once_with()

    def test_update_local_package_manager_cache_does_not_update_cache_if_cache_too_recent(self):
        self.file_age_in_seconds.return_value -= 1

        update_local_package_manager_cache_if_necessary()

        self.assertFalse(self.update_package_manager_cache.called)

    def test_update_local_package_manager_cache_does_not_touch_the_updated_file_if_cache_not_updated(self):
        self.file_age_in_seconds.return_value -= 1

        update_local_package_manager_cache_if_necessary()

        self.assertFalse(self.path.called)
