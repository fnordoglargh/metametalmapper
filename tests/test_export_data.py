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


if __name__ == '__main__':
    unittest.main()
