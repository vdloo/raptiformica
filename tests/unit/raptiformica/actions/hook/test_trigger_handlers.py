from raptiformica.actions.hook import trigger_handlers
from tests.testcase import TestCase


class TestTriggerHandlers(TestCase):
    def setUp(self):
        self.log = self.set_up_patch('raptiformica.actions.hook.log')
        self.fire_hooks = self.set_up_patch('raptiformica.actions.hook.fire_hooks')

    def test_trigger_handlers_logs_message(self):
        trigger_handlers('some_hook')

        self.assertEqual(2, self.log.info.call_count)

    def test_trigger_handlers_fires_hooks_for_passed_hook_name(self):
        trigger_handlers('some_hook')

        self.fire_hooks.assert_called_once_with('some_hook')
