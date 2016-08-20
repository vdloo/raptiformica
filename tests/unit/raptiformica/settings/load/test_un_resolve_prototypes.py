from raptiformica.settings.load import un_resolve_prototypes
from tests.testcase import TestCase


class TestUnResolvePrototype(TestCase):
    def setUp(self):
        self.prototypes = {
            'prototype1': {
                'prototype': {
                    'key1': {'content': 'value1'},
                    'resolved_prototype_name': 'prototype2'
                },

            },
            'prototype2': {
                'key1': {'content': 'value1'}
            },
        }
        self.config = {
            'prototype': {
                'prototype': {
                    'key1': {
                        'content': 'value1'
                    },
                    'resolved_prototype_name': 'prototype2'
                },
                'resolved_prototype_name': 'prototype1'
            },
            'module_prototype': self.prototypes
        }

    def test_un_resolve_prototype_un_resolves_prototypes(self):
        ret = un_resolve_prototypes(self.prototypes, self.config)

        expected_config = {
            'module_prototype': {
                'prototype1': {'prototype': 'prototype2'},
                'prototype2': {'key1': {'content': 'value1'}}
            },
            'prototype': 'prototype1'
        }
        self.assertEqual(ret, expected_config)
