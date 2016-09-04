from raptiformica.settings.load import loop_config
from tests.testcase import TestCase


class TestLoopConfig(TestCase):
    def setUp(self):
        self.config = {
            'key1': {
                'key2': 'value2',
                'key3': 'value3'
            },
            'key4': {
                'key5': {
                    'key6': 'value6'
                }
            }
        }

    def test_loop_config_runs_callback_for_each_value(self):
        arguments = list()

        loop_config(
            self.config,
            path='some/path/',
            callback=lambda p, k, v: arguments.append((p, k, v))
        )

        expected_arguments = [
            ('some/path/key4/key5', 'key6', 'value6'),
            ('some/path/key1', 'key2', 'value2'),
            ('some/path/key1', 'key3', 'value3')
        ]
        self.assertCountEqual(
            arguments,
            expected_arguments
        )