import unittest
from metalCrawler import *
import genre

class TestGenreCutting(unittest.TestCase):

    def test_cutting(self):
        result = genre.split_genres('Black Metal')
        expected_cut = ['Black']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Pagan Black Metal (early), Death Metal (later)')
        expected_cut = ['Pagan Black', 'Death']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Death Metal (early), Black Metal (mid), Black/Heavy/Speed Metal (later)')
        expected_cut = ['Death', 'Black', 'Heavy', 'Speed']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Symphonic Black/Death Metal (early), Melodic Death Metal (later)')
        expected_cut = ['Symphonic Black', 'Death', 'Melodic Death']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Experimental Black Metal/Dark Ambient')
        expected_cut = ['Experimental Black', 'Dark Ambient']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Melodic Power/Speed Metal/Rock')
        expected_cut = ['Melodic Power', 'Speed', 'Rock']
        self.assertEqual(expected_cut, result)




