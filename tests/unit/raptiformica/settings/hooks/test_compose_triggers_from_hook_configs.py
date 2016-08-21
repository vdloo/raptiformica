from raptiformica.settings.hooks import compose_triggers_from_hook_configs
from tests.testcase import TestCase


class TestComposeTriggersFromHookConfigs(TestCase):
    def setUp(self):
        self.get_config_value = self.set_up_patch(
            'raptiformica.settings.hooks.get_config_value'
        )
        self.get_config_value.side_effect = [
            'predicate1',
            'command1',
            'predicate2',
            'command2'
        ]
        self.hook_configs = [{'some': 'hook'}, {'configs': 'in a list'}]

    def test_compose_triggers_from_hook_configs_returns_composed_triggers(self):
        ret = list(compose_triggers_from_hook_configs(self.hook_configs))

        expected_list_of_hooks = [
            {
                'predicate': 'predicate1',
                'command': 'command1'
            },
            {
                'predicate': 'predicate2',
                'command': 'command2'
            }
        ]
        self.assertListEqual(ret, expected_list_of_hooks)
