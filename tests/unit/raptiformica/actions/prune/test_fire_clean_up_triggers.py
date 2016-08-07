from mock import call

from raptiformica.actions.prune import fire_clean_up_triggers
from tests.testcase import TestCase


class TestFireCleanUpTriggers(TestCase):
    def setUp(self):
        self.clean_up_triggers = [
            ('directory1',
             './bin/detect/stale/command1',
             './bin/clean/up/stale/command1'),
            ('directory2',
             './bin/detect/stale/command2',
             './bin/clean/up/stale/command2'),
            ('directory3',
             './bin/detect/stale/command3',
             './bin/clean/up/stale/command3')
        ]
        self.check_if_instance_is_stale = self.set_up_patch(
            'raptiformica.actions.prune.check_if_instance_is_stale'
        )
        self.clean_up_stale_instance = self.set_up_patch(
            'raptiformica.actions.prune.clean_up_stale_instance'
        )
        self.rmtree = self.set_up_patch('raptiformica.actions.prune.rmtree')

    def test_fire_clean_up_triggers_checks_if_instances_are_stale(self):
        fire_clean_up_triggers(self.clean_up_triggers)

        expected_calls = [
            call('directory1', './bin/detect/stale/command1'),
            call('directory2', './bin/detect/stale/command2'),
            call('directory3', './bin/detect/stale/command3'),
        ]
        self.assertCountEqual(
            self.check_if_instance_is_stale.mock_calls, expected_calls
        )

    def test_fire_clean_up_triggers_cleans_up_stale_instances(self):
        # pretend the first and last instance are stale
        self.check_if_instance_is_stale.side_effect = [True, False, True]

        fire_clean_up_triggers(self.clean_up_triggers)

        expected_calls = [
            call('directory1', './bin/clean/up/stale/command1'),
            call('directory3', './bin/clean/up/stale/command3'),
        ]
        self.assertCountEqual(
            self.clean_up_stale_instance.mock_calls, expected_calls
        )

    def test_fire_clean_up_triggers_cleans_up_stale_checkout_directories(self):
        # pretend the first and second instance are stale
        self.check_if_instance_is_stale.side_effect = [True, True, False]

        fire_clean_up_triggers(self.clean_up_triggers)

        expected_calls = [
            call('directory1', ignore_errors=True),
            call('directory2', ignore_errors=True),
        ]
        self.assertCountEqual(
            self.rmtree.mock_calls,
            expected_calls
        )
