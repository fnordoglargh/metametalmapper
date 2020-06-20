import unittest

from graph.report import check_bands_in_country

band_links_expected = [
    'Dimmu_Borgir/69',
    'Ancient/772',
    'Immortal/75',
    'Emperor/30',
    'Arcturus/292'
]

band_links_more = [
    'Cryptopsy/17',
    'Dimmu_Borgir/69',
    'Ancient/772',
    'Immortal/75',
    'Emperor/30',
    'Arcturus/292'
]

band_links_less = [
    'Dimmu_Borgir/69',
    'Ancient/772',
    'Emperor/30',
    'Arcturus/292'
]

true_kings = 'true_kings'
band_links_expected.sort()
band_links_more.sort()
band_links_less.sort()


class MyTestCase(unittest.TestCase):
    def test_bands_valid(self):
        result_set = check_bands_in_country(true_kings, band_links_expected, '../data')
        self.assertEqual(result_set, ([], [], 'Not a country: "true_kings"'))

    def test_bands_more_than_expected(self):
        result_set = check_bands_in_country(true_kings, band_links_more, '../data')
        self.assertEqual(result_set, ([], ['Cryptopsy/17'], 'Not a country: "true_kings"'))

    def test_bands_less_than_expected(self):
        result_set = check_bands_in_country(true_kings, band_links_less, '../data')
        self.assertEqual(result_set, (['Immortal/75'], [], 'Not a country: "true_kings"'))

    def test_bands_equal_length_but_different(self):
        result_set = check_bands_in_country('band_links_less_and missing', band_links_expected, '../tests')
        self.assertEqual(result_set, (['Cryptopsy/17'],
                                      ['Arcturus/292', 'Dimmu_Borgir/69'],
                                      'Not a country: "band_links_less_and missing"'))

    def test_invalid_file(self):
        result_set = check_bands_in_country('does_not_exist', band_links_expected, '../tests')
        self.assertEqual(result_set, None)


if __name__ == '__main__':
    unittest.main()
