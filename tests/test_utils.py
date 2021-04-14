import unittest

from service_catalog.utils import str_to_bool


class TestUtils(unittest.TestCase):

    def test_str_to_bool(self):
        self.assertTrue(str_to_bool("True"))
        self.assertTrue(str_to_bool("true"))
        self.assertTrue(str_to_bool(True))
        self.assertTrue(str_to_bool(1))
        self.assertTrue(str_to_bool("1"))
        self.assertFalse(str_to_bool("False"))
        self.assertFalse(str_to_bool("false"))
        self.assertFalse(str_to_bool(False))
        self.assertFalse(str_to_bool(0))
        self.assertFalse(str_to_bool("0"))
