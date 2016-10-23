from raptiformica.settings import MODULES_DIR
from raptiformica.settings import USER_MODULES_DIR
from raptiformica.settings.load import on_disk_mapping
from tests.testcase import TestCase


class TestOnDiskMapping(TestCase):
    def setUp(self):
        self.load_module_configs = self.set_up_patch(
            'raptiformica.settings.load.load_module_configs'
        )
        self.load_module_configs.return_value = [
            {'some': {'module': {'config': 'some_modue_value'}}},
            {'some': {'other': {'module': {'config': 'some_other_module_value'}}}},
            {'yet': {'another': {'module': {'config': "yet_another_module_value"}}}}
        ]

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

    def test_on_disk_mapping_returns_mapped_configs(self):
        ret = on_disk_mapping()

        expected_mapping = {
            'raptiformica/some/module/config': 'some_modue_value',
            'raptiformica/some/other/module/config': 'some_other_module_value',
            'raptiformica/yet/another/module/config': 'yet_another_module_value'
        }
        self.assertEqual(ret, expected_mapping)
