import unittest
from export_data import ExportData


class TestGenderLoading(unittest.TestCase):

    def test_valid_entry(self):
        data = ExportData()
        result = data.add_gender_country(country='US', gender='M', count=10)
        self.assertEqual(True, result)

    def test_invalid_country(self):
        data = ExportData()
        result = data.add_gender_country(country='0', gender='M', count=10)
        self.assertEqual(False, result)

    def test_invalid_gender(self):
        data = ExportData()
        result = data.add_gender_country(country='US', gender='0', count=10)
        self.assertEqual(False, result)

    def test_invalid_gender_and_country(self):
        data = ExportData()
        result = data.add_gender_country(country='0', gender='0', count=10)
        self.assertEqual(False, result)


class TestGenreLoading(unittest.TestCase):

    def test_valid_entry(self):
        data = ExportData()
        result = data.add_genre_country(country='US', genres=['Death', 'Black'], count=10)
        self.assertEqual(True, result)
        result = data.add_genre_country(country='US', genres=['Power'], count=66)
        self.assertEqual(True, result)
        result = data.add_genre_country(country='DK', genres=['Black'], count=11)
        self.assertEqual(True, result)
        expected_data = {
            'US': {
                'Death': 10,
                'Black': 10,
                'Power': 66
            },
            'DK': {
                'Black': 11
            }
        }
        self.assertEqual(expected_data, data.genres)

    def test_invalid_country(self):
        data = ExportData()
        result = data.add_genre_country(country='0', genres=['Death', 'Black'], count=10)
        self.assertEqual(False, result)
        expected_data = {}
        self.assertEqual(expected_data, data.genres)

    def test_invalid_genre(self):
        data = ExportData()
        result = data.add_genre_country(country='US', genres=[], count=10)
        self.assertEqual(False, result)
        expected_data = { 'US': {} }
        self.assertEqual(expected_data, data.genres)

    def test_invalid_genre_and_country(self):
        data = ExportData()
        result = data.add_genre_country(country='0', genres=['Death', 'Black'], count=10)
        self.assertEqual(False, result)
        expected_data = {}
        self.assertEqual(expected_data, data.genres)


if __name__ == '__main__':
    unittest.main()
