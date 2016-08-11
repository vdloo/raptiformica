from raptiformica.utils import transform_key_in_dict_recursively
from tests.testcase import TestCase


class TestTransformKeyInDictRecursively(TestCase):
    def setUp(self):
        self.dictionary = {
            'key': {
                'needle': 'value1'
            },
            'needle': 'value2'
        }

    def test_transform_key_in_dict_recursively_returns_dict_if_identity_function_is_used_to_transform(self):
        ret = transform_key_in_dict_recursively(self.dictionary, 'needle')

        self.assertEqual(ret, self.dictionary)

    def test_transform_key_in_dict_recursively_returns_transformed_dict(self):
        ret = transform_key_in_dict_recursively(self.dictionary, 'needle', lambda *args: None)

        expected_dict = {
            'key': {
                'needle': None
            },
            'needle': None
        }
        self.assertEqual(ret, expected_dict)
