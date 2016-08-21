from raptiformica.settings.hooks import gather_hook_configs
from tests.testcase import TestCase


class TestGatherHookConfigs(TestCase):
    def setUp(self):
        self.load_config = self.set_up_patch(
            'raptiformica.settings.hooks.load_config'
        )
        self.load_config.return_value = {
            "platform_types": {
                "default": {
                    "hooks": {
                        "prototype": {
                            "ensure_second_machine": {
                                "after_mesh": {
                                    "prototype": {
                                        "command": {
                                            "content": "this is command 1"
                                        },
                                        "predicate": {
                                            "content": "this is predicate 1"
                                        },
                                        "resolved_prototype_name": "ensure_consensus_trigger_prototype"
                                    }
                                }
                            },
                            "ensure_third_machine": {
                                "after_mesh": {
                                    "prototype": {
                                        "command": {
                                            "content": "this is command 2"
                                        },
                                        "predicate": {
                                            "content": "this is predicate 2"
                                        },
                                        "resolved_prototype_name": "ensure_consensus_trigger_prototype"
                                    }
                                }
                            },
                            "ensure_fourth_machine": {
                                "not_after_mesh": {
                                    "prototype": {
                                        "command": {
                                            "content": "this is command 3"
                                        },
                                        "predicate": {
                                            "content": "this is predicate 3"
                                        },
                                        "resolved_prototype_name": "ensure_consensus_trigger_prototype"
                                    }
                                }
                            },
                            "resolved_prototype_name": "default_platform_type_hooks"
                        }
                    }
                }
            }
        }

    def test_gather_hook_configs_raises_value_error_if_no_such_platform_type_in_config(self):
        with self.assertRaises(ValueError):
            gather_hook_configs('after_mesh', platform_type='does_not_exist')

    def test_gather_hook_configs_loads_config(self):
        ret = gather_hook_configs('after_mesh', platform_type='default')

        expected_hook_configs = [
            {'prototype': {'predicate': {'content': 'this is predicate 1'},
                           'command': {'content': 'this is command 1'},
                           'resolved_prototype_name': 'ensure_consensus_trigger_prototype'}},
            {'prototype': {'predicate': {'content': 'this is predicate 2'},
                           'command': {'content': 'this is command 2'},
                           'resolved_prototype_name': 'ensure_consensus_trigger_prototype'}}
        ]
        self.assertCountEqual(ret, expected_hook_configs)
