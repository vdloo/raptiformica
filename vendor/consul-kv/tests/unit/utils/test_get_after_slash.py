from consul_kv.utils import get_after_slash
from tests.testcase import TestCase


class TestGetAfterSlash(TestCase):
    def test_get_after_slash_gets_part_of_string_after_slash(self):
        ret = get_after_slash("this/is/the/string")

        self.assertEqual(ret, 'is/the/string')

    def test_get_after_slash_gets_empty_string_if_no_slash(self):
        ret = get_after_slash("this_is_the_entire_string")

        self.assertEqual(ret, '')
