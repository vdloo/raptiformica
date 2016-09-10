from raptiformica.settings import MODULES_DIR
from raptiformica.settings import USER_MODULES_DIR
from raptiformica.settings.load import on_disk_mapping
from tests.testcase import TestCase


class TestOnDiskMapping(TestCase):
    def setUp(self):
        self.load_module_configs = self.set_up_patch(
            'raptiformica.settings.load.load_module_configs'
        )
        self.map_configs = self.set_up_patch(
            'raptiformica.settings.load.map_configs'
        )

    def test_on_disk_mapping_loads_module_configs(self):
        on_disk_mapping()

        self.load_module_configs.assert_called_once_with(
            module_dirs=(MODULES_DIR, USER_MODULES_DIR)
        )

    def test_on_disk_mapping_loads_specified_module_configs(self):
        on_disk_mapping(module_dirs=('some/directory',))

        self.load_module_configs.assert_called_once_with(
            module_dirs=('some/directory',)
        )

    def test_on_disk_mapping_maps_configs(self):
        on_disk_mapping()

        self.map_configs.assert_called_once_with(
            self.load_module_configs.return_value
        )

    def test_on_disk_mapping_returns_mapping(self):
        ret = on_disk_mapping()

        self.assertEqual(self.map_configs.return_value, ret)

