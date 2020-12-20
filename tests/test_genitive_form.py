import unittest
from global_helpers import append_genitive_s


class TestEnglishGenitive(unittest.TestCase):
    def test_normal_genitive_form(self):
        test_text = "England"
        expected = "England's"

        self.assertEqual(expected, append_genitive_s(test_text))

    def test_ending_with_s(self):
        test_text = "Comoros"
        expected = "Comoros'"

        self.assertEqual(expected, append_genitive_s(test_text))

        test_text = "Felix"
        expected = "Felix'"

        self.assertEqual(expected, append_genitive_s(test_text))

        test_text = "Agnez"
        expected = "Agnez'"

        self.assertEqual(expected, append_genitive_s(test_text))

    def test_empty_input(self):
        test_text = ""
        expected = ""

        self.assertEqual(expected, append_genitive_s(test_text))
