from raptiformica.settings.meshnet import ensure_shared_secret
from tests.testcase import TestCase


class TestEnsureSharedSecret(TestCase):
    def setUp(self):
        self.config = {
            'meshnet': {
                'consul': {'password': 'the_shared_secret'}
            }
        }
        self.uuid = self.set_up_patch('raptiformica.settings.meshnet.uuid')
        self.uuid.uuid4.return_value.hex = 'the_shared_secret'

    def test_ensure_shared_secret_does_not_update_secret_if_it_already_exists(self):
        ret = ensure_shared_secret(self.config, 'consul')

        self.assertEquals(ret, self.config)

    def test_ensure_shared_secret_generates_new_shared_secret_if_it_does_not_exist(self):
        config = {'meshnet': {'consul': {}}}

        ret = ensure_shared_secret(config, 'consul')

        self.assertEquals(ret, self.config)
