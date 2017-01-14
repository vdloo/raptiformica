from raptiformica.settings import conf
from raptiformica.settings.hooks import collect_hooks
from tests.testcase import TestCase


class TestCollectHooks(TestCase):
    def setUp(self):
        self.get_first_platform_type = self.set_up_patch(
            'raptiformica.settings.hooks.get_first_platform_type'
        )
        self.get_first_platform_type.return_value = 'default'
        self.get_config = self.set_up_patch(
            'raptiformica.settings.hooks.get_config'
        )
        self.get_config.return_value = {
            conf().KEY_VALUE_PATH: {
                'platform': {
                    'default': {
                        'hooks': {
                            'after_mesh': {
                                'hook_1': {
                                    'predicate': '/bin/test1',
                                    'command': '/bin/command'
                                },
                                'hook_2': {
                                    'predicate': '/bin/test2',
                                },
                            }
                        }
                    },
                    'no_hooks_platform': {}
                }
            }
        }

    def test_collect_hooks_gets_first_platform_type(self):
        collect_hooks('after_mesh')

        self.get_first_platform_type.assert_called_once_with()

    def test_collect_hooks_does_not_get_first_platform_type_if_platform_type_specified(self):
        collect_hooks('after_mesh', platform_type='default')

        self.assertFalse(self.get_first_platform_type.called)

    def test_collect_hooks_gets_config(self):
        collect_hooks('after_mesh')

        self.get_config.assert_called_once_with()

    def test_collect_hooks_returns_empty_list_if_no_matching_hooks(self):
        ret = collect_hooks('does_not_exist')

        self.assertCountEqual(ret, tuple())

    def test_collect_hooks_returns_list_of_hooks(self):
        ret = collect_hooks('after_mesh')

        expected_hooks = [
            {'predicate': '/bin/test1', 'command': '/bin/command'},
            {'predicate': '/bin/test2', 'command': '/bin/true'}

        ]
        self.assertCountEqual(ret, expected_hooks)

    def test_collect_hooks_raises_keyerror_if_no_such_platform(self):
        with self.assertRaises(KeyError):
            collect_hooks('after_mesh', platform_type='does_not_exist')

    def test_collect_hooks_returns_empty_list_if_no_hooks_in_platform(self):
        ret = collect_hooks('no_hooks_platform')

        self.assertCountEqual(ret, tuple())
