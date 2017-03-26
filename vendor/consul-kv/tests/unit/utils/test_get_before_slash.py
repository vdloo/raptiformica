from consul_kv.utils import get_before_slash
from tests.testcase import TestCase


class TestGetBeforeSlash(TestCase):
    def test_get_before_slash_gets_part_of_string_before_slash(self):
        ret = get_before_slash("this/is/the/string")

        self.assertEqual(ret, 'this')

    def test_get_before_slash_gets_entire_string_if_no_slash(self):
        ret = get_before_slash("this_is_the_entire_string")

        self.assertEqual(ret, 'this_is_the_entire_string')
