import unittest
import genre

class TestGenreCutting(unittest.TestCase):

    def test_cutting(self):
        result = genre.split_genres('Black Metal')
        expected_cut = ['Black']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Pagan Black Metal (early), Death Metal (later)')
        expected_cut = ['Pagan Black', 'Black', 'Folk/Viking/Pagan', 'Death']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Death Metal (early), Black Metal (mid), Black/Heavy/Speed Metal (later)')
        expected_cut = ['Death', 'Black', 'Heavy', 'Speed']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Symphonic Black/Death Metal (early), Melodic Death Metal (later)')
        expected_cut = ['Symphonic Black', 'Black', 'Symphonic', 'Death', 'Melodic Death']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Experimental Black Metal/Dark Ambient')
        expected_cut = ['Experimental Black', 'Black', 'Experimental/Avant-garde', 'Dark Ambient']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Melodic Power/Speed Metal/Rock')
        expected_cut = ['Melodic Power', 'Power', 'Speed', 'Rock']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Industrial Metal')
        expected_cut = ['Industrial', 'Electronic/Industrial']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Electronic Progressive Death/Thrash Metal')
        expected_cut = ['Electronic Progressive Death', 'Death', 'Electronic/Industrial', 'Progressive', 'Thrash']
        self.assertEqual(expected_cut, result)

        result = genre.split_genres('Melodic Death/Doom Metal (early), Industrial/Gothic Metal (mid), Melodic Metalcore (later)')
        expected_cut = ['Melodic Death', 'Death', 'Doom', 'Doom/Stoner/Sludge', 'Industrial', 'Electronic/Industrial', 'Gothic', 'Melodic Metalcore', 'Metalcore/Deathcore']
        self.assertEqual(expected_cut, result)




