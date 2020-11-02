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


if __name__ == '__main__':
    unittest.main()
