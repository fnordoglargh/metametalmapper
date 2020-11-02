import unittest
from country_helper import split_locations


class TestLocationCutting(unittest.TestCase):

    def test_country_cutting(self):
        location_ma = ''
        expected = ['']
        self.assertEqual(expected, split_locations(location_ma))

        location_ma = 'N/A'
        expected = ['N/A']
        self.assertEqual(expected, split_locations(location_ma))

        location_ma = 'Los Angeles/San Francisco, California'
        expected = ['Los Angeles', 'California']
        self.assertEqual(expected, split_locations(location_ma))

        location_ma = 'Kolbotn, Viken (early); Oslo (mid); Vinterbro, Viken / Trysil, Innlandet (later)'
        expected = ['Kolbotn', 'Viken']
        self.assertEqual(expected, split_locations(location_ma))

        location_ma = 'Hong Kong (early); Oakville, Ontario, Canada (mid); Helsinki, Uusimaa, Finland (later)'
        expected = ['Hong Kong']
        self.assertEqual(expected, split_locations(location_ma))

        # Test case #5
        location_ma = 'Roodeport, Gauteng / Durban, KwaZulu-Natal'
        expected = ['Roodeport', 'Gauteng']
        self.assertEqual(expected, split_locations(location_ma))

        location_ma = 'Helderberg (early)/Cape Town (later), Western Cape'
        expected = ['Helderberg', 'Western Cape']
        self.assertEqual(expected, split_locations(location_ma))

        # Test case #7
        location_ma = '	Lisbon, Portugal / Sollentuna, Sweden (early), Lisbon, Lisbon (later)'
        expected = ['Lisbon']
        self.assertEqual(expected, split_locations(location_ma))

        # Constructed case.
        location_ma = 'Los Angeles/San Francisco, California/haha/fnord(early)'
        expected = ['Los Angeles', 'California']
        self.assertEqual(expected, split_locations(location_ma))


if __name__ == '__main__':
    unittest.main()
