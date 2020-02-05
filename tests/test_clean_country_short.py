import unittest
from country_helper import clean_short_links


class TestCleanCountryShort(unittest.TestCase):
    def test_cleaning(self):
        test_data = [
            'US',    # One valid country short link.
            'GB,US',  # Two valid
            'AA',  # One invalid
            'SY,AA', # One valid, one invalid
            '', # Empty
            ',', # Invalid: Two empty elements
            ', GB,' # One valid
        ]

        expected_results = [
            ['US'],
            ['GB', 'US'],
            [],
            ['SY'],
            [],
            [],
            ['GB']
        ]

        for i in range(0, len(test_data)):
            self.assertEqual(clean_short_links(test_data[i]), expected_results[i])


if __name__ == '__main__':
    unittest.main()
