from raptiformica.settings.hooks import collect_hooks
from tests.testcase import TestCase


class TestCollectHooks(TestCase):
    def setUp(self):
        self.gather_hook_configs = self.set_up_patch(
            'raptiformica.settings.hooks.gather_hook_configs'
        )
        self.get_first_platform_type = self.set_up_patch(
            'raptiformica.settings.hooks.get_first_platform_type'
        )
        self.compose_triggers_from_hook_configs = self.set_up_patch(
            'raptiformica.settings.hooks.compose_triggers_from_hook_configs'
        )

    def test_collect_hooks_gathers_hook_configs(self):
        collect_hooks('after_mesh')

        self.gather_hook_configs.assert_called_once_with(
            'after_mesh',
            platform_type=self.get_first_platform_type.return_value
        )

    def test_collect_hooks_gathers_hook_configs_for_passed_platform_type(self):
        collect_hooks('after_mesh', platform_type='default')

        self.gather_hook_configs.assert_called_once_with(
                'after_mesh',
                platform_type='default'
        )

    def test_collect_hooks_composes_triggers_from_hook_configs(self):
        collect_hooks('after_mesh')

        self.compose_triggers_from_hook_configs.assert_called_once_with(
            self.gather_hook_configs.return_value
        )

    def test_collect_hooks_returns_composed_triggers(self):
        ret = collect_hooks('after_mesh')

        self.assertEqual(
            ret, self.compose_triggers_from_hook_configs.return_value
        )
