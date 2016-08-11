from raptiformica.settings.load import resolve_prototypes
from tests.testcase import TestCase


class TestResolvePrototype(TestCase):
    def setUp(self):
        self.prototypes = {
            'prototype1': {'prototype': 'prototype2'},
            'prototype2': {'key1': {'content': 'value1'}},
        }
        self.config = {
            'prototype': 'prototype1'
        }

    def test_resolve_prototype_resolves_prototypes(self):
        ret = resolve_prototypes(self.prototypes, self.config)

        expected_config = {
            'prototype': {
                'prototype': {
                    'key1': {
                        'content': 'value1'
                    }
                }
            }
        }
        self.assertEqual(ret, expected_config)
