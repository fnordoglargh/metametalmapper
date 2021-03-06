import unittest
import genre


class TestGenreCutting(unittest.TestCase):

    def test_cutting(self):
        test_strings = [
            ('Black Metal',
             ['Black']),
            ('Pagan Black Metal (early), Death Metal (later)',
             ['Pagan Black', 'Black', 'Folk/Viking/Pagan', 'Death']),
            ('Death Metal (early), Black Metal (mid), Black/Heavy/Speed Metal (later)',
             ['Death', 'Black', 'Heavy', 'Speed']),
            ('Symphonic Black/Death Metal (early), Melodic Death Metal (later)',
             ['Symphonic Black', 'Black', 'Symphonic', 'Death', 'Melodic Death']),
            ('Experimental Black Metal/Dark Ambient',
             ['Experimental Black', 'Black', 'Experimental/Avant-garde', 'Dark Ambient']),
            ('Melodic Power/Speed Metal/Rock',
             ['Melodic Power', 'Power', 'Speed', 'Rock']),
            ('Industrial Metal',
             ['Industrial', 'Electronic/Industrial']),
            ('Electronic Progressive Death/Thrash Metal',
             ['Electronic Progressive Death', 'Death', 'Electronic/Industrial', 'Progressive', 'Thrash']),
            ('Melodic Death/Doom Metal (early), Industrial/Gothic Metal (mid), Melodic Metalcore (later)',
             ['Melodic Death', 'Death', 'Doom', 'Doom/Stoner/Sludge', 'Industrial', 'Electronic/Industrial', 'Gothic', 'Melodic Metalcore', 'Metalcore/Deathcore']),
            # ('Symphonic/Atmospheric Black Metal',
            #  ['Symphonic Black', 'Atmospheric Black', 'Black']),
            ('Progressive Death Metal, Progressive Rock/Metal (on Screaming Machines)',
             ['Progressive Death', 'Death', 'Progressive', 'Progressive Rock']),
            ('Death Metal (early); Black Metal (mid); Black/Heavy/Speed Metal (later)',
             ['Death', 'Black', 'Heavy', 'Speed']),
            ('Atmospheric Black Metal (early); Avant-garde Progressive Metal (later)',
             ['Atmospheric Black', 'Black', 'Avant-garde Progressive', 'Experimental/Avant-garde', 'Progressive']),
            ('Brutal/Technical Death Metal, Deathcore (2008)',
             ['Brutal', 'Technical Death', 'Death', 'Deathcore', 'Metalcore/Deathcore'])
        ]

        for test in test_strings:
            result = genre.split_genres(test[0])
            self.assertEqual(test[1], result)
