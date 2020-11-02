import unittest
from datetime import date, datetime
from metal_crawler import make_active_list


class TestBandActivityConversion(unittest.TestCase):
    def test_happy_case(self):
        valid_dates = ['1980-1981']
        expected_result = [date(1980, 1, 1), date(1981, 12, 31)]
        self.assertEqual(expected_result, make_active_list(valid_dates))

        valid_dates.append('1990-1993')
        expected_result.append(date(1990, 1, 1))
        expected_result.append(date(1993, 12, 31))
        self.assertEqual(expected_result, make_active_list(valid_dates))

        valid_dates.append('2000-present')
        expected_result.append(date(2000, 1, 1))
        expected_result.append(date(date.today().year, 12, 31))
        self.assertEqual(expected_result, make_active_list(valid_dates))

    def test_error_cases(self):
        invalid_date = ['?-2000']
        expected_result = []
        self.assertEqual(expected_result, make_active_list(invalid_date))

        invalid_date = ['2000-?']
        expected_result = []
        self.assertEqual(expected_result, make_active_list(invalid_date))

        invalid_date = ['N/A']
        expected_result = []
        self.assertEqual(expected_result, make_active_list(invalid_date))

        invalid_date = ['gnsdofhn']
        expected_result = []
        self.assertEqual(expected_result, make_active_list(invalid_date))

    def mixed_cases(self):
        invalid_date = ['?-2000', '2001-2001', 'argl', '2001-asfd', 2003, '2003-?']
        expected_result = [date(2001, 1, 1), date(2001, 12, 31), date(2003, 1, 1), date(date.today().year, 12, 31)]
        self.assertEqual(expected_result, make_active_list(invalid_date))


if __name__ == '__main__':
    unittest.main()
