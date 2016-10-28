from raptiformica.settings import KEY_VALUE_PATH
from raptiformica.settings.types import list_types_from_config
from tests.testcase import TestCase


class TestListTypesFromConfig(TestCase):
    def setUp(self):
        self.get_config = self.set_up_patch(
            'raptiformica.settings.types.get_config'
        )
        self.get_config.return_value = {
            KEY_VALUE_PATH: {
                'server': {
                    'headless': {},
                    'workstation': {}
                }
            }
        }

    def test_list_types_from_config_gets_config(self):
        list_types_from_config('server')

        self.get_config.assert_called_once_with()

    def test_list_types_from_config_lists_types_from_config(self):
        ret = list_types_from_config('server')

        self.assertCountEqual(ret, ['headless', 'workstation'])

    def test_list_types_from_config_raises_keyerror_if_type_is_not_configured(self):
        with self.assertRaises(KeyError):
            list_types_from_config('compute')

