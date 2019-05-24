import unittest
from metalCrawler import *


class TestInstrumentCutting(unittest.TestCase):

    def test_cutting2(self):
        result = cut_instruments2('Guitars')
        expected_cut = [('Guitars', [])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2('Guitars (earlier)')
        expected_cut = [('Guitars (earlier)', [])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2('Guitars (Session) (earlier), Vocals (Session) (later)')
        expected_cut = [('Guitars (Session) (earlier)', []),
                        ('Vocals (Session) (later)', [])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2('Bass (1989-2004)')
        expected_cut = [('Bass', [(1989, 2004)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2('Bass (Session) (1989-2004)')
        expected_cut = [('Bass (Session)', [(1989, 2004)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2('Bass (1989-2004, 2007, 2017-present)')
        expected_cut = [('Bass', [(1989, 2004), (2007, 2007), (2017, 'present')])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2('Guitars(1991-1993), Bass(1993)')
        expected_cut = [('Guitars', [(1991, 1993)]),
                        ('Bass', [(1993, 1993)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2('Bass (1989-2004, 2017-present), Flute, Triangle (1989-2004)')
        expected_cut = [('Bass', [(1989, 2004), (2017, 'present')]),
                        ('Flute, Triangle', [(1989, 2004)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments2(
            'Drums, Vocals (additional)(1970, 1972-1973, 1987-present), Bass, Guitars (additional)(1993-present)')
        expected_cut = [('Drums, Vocals (additional)', [(1970,1970), (1972, 1973), (1987, 'present')]),
                        ('Bass, Guitars (additional)', [(1993, 'present')])]
        self.assertEqual(expected_cut, result)


