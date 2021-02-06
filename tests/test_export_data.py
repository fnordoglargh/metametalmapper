import unittest
from export_data import ExportData, ExportGender


class TestGenderLoading(unittest.TestCase):

    def test_valid_entry(self):
        data = ExportData()
        result = data.add_gender_country(band_origin='US', artist_origin='US', gender='M', count=77)
        self.assertEqual(True, result)
        result = data.add_gender_country(band_origin='US', artist_origin='US', gender='F', count=7)
        self.assertEqual(True, result)
        expected_data = ExportGender()
        expected_data.genders['US'] = {}
        expected_data.genders['US']['M'] = 77
        expected_data.genders['US']['F'] = 7
        expected_data.totals['M'] = 77
        expected_data.totals['F'] = 7
        self.assertEqual(expected_data, data.genders['US'])

    def test_invalid_origins(self):
        data = ExportData()
        result = data.add_gender_country(band_origin='0', artist_origin='US', gender='M', count=10)
        self.assertEqual(False, result)
        expected_data = {}
        self.assertEqual(expected_data, data.genders)

        data = ExportData()
        result = data.add_gender_country(band_origin='US', artist_origin='0', gender='M', count=10)
        self.assertEqual(False, result)
        expected_data = {}
        self.assertEqual(expected_data, data.genders)

        data = ExportData()
        result = data.add_gender_country(band_origin='0', artist_origin='0', gender='M', count=10)
        self.assertEqual(False, result)
        expected_data = {}
        self.assertEqual(expected_data, data.genders)

    def test_invalid_gender(self):
        data = ExportData()
        result = data.add_gender_country(band_origin='US', artist_origin='US', gender='0', count=10)
        self.assertEqual(False, result)
        expected_data = {'US': ExportGender()}
        expected_data['US'].genders['US'] = {}
        self.assertEqual(expected_data, data.genders)

    def test_invalid_gender_and_country(self):
        data = ExportData()
        result = data.add_gender_country(band_origin='0', artist_origin='0', gender='0', count=10)
        self.assertEqual(False, result)
        expected_data = {}
        self.assertEqual(expected_data, data.genders)

    def test_mixed_data(self):
        data = ExportData()
        result = data.add_gender_country(band_origin='US', artist_origin='US', gender='M', count=77)
        self.assertEqual(True, result)
        result = data.add_gender_country(band_origin='US', artist_origin='US', gender='F', count=7)
        self.assertEqual(True, result)
        expected_data = {'US': ExportGender()}
        expected_data['US'].genders['US'] = {}
        expected_data['US'].genders['US']['M'] = 77
        expected_data['US'].genders['US']['F'] = 7
        expected_data['US'].totals['M'] = 77
        expected_data['US'].totals['F'] = 7
        self.assertEqual(expected_data, data.genders)
        # Gender invalid.
        result = data.add_gender_country(band_origin='DE', artist_origin='DK', gender='0', count=10)
        self.assertEqual(False, result)
        expected_data['DE'] = ExportGender()
        expected_data['DE'].genders['DK'] = {}
        self.assertEqual(expected_data, data.genders)
        # Negative count sets number to 0.
        result = data.add_gender_country(band_origin='DE', artist_origin='DK', gender='F', count=-100)
        self.assertEqual(False, result)
        expected_data['DE'].genders['DK']['F'] = 0
        expected_data['DE'].totals['F'] = 0
        self.assertEqual(expected_data, data.genders)


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
            'Total': {
                'Death': 10,
                'Black': 21,
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
        expected_data = {'Total': {}, 'US': {}}
        self.assertEqual(expected_data, data.genres)

    def test_invalid_genre_and_country(self):
        data = ExportData()
        result = data.add_genre_country(country='0', genres=['Death', 'Black'], count=10)
        self.assertEqual(False, result)
        expected_data = {}
        self.assertEqual(expected_data, data.genres)


if __name__ == '__main__':
    unittest.main()
