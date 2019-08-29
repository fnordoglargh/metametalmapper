import unittest
from metalCrawler import *


class TestInstrumentCutting(unittest.TestCase):

    def test_cutting(self):
        result = cut_instruments('Guitars')
        expected_cut = [('Guitars', [])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Guitars (earlier)')
        expected_cut = [('Guitars (earlier)', [])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Guitars (Session) (earlier), Vocals (Session) (later)')
        expected_cut = [('Guitars (Session) (earlier)', []),
                        ('Vocals (Session) (later)', [])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Bass (1989-2004)')
        expected_cut = [('Bass', [(1989, 2004)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Bass (Session) (1989-2004)')
        expected_cut = [('Bass (Session)', [(1989, 2004)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Bass (1989-2004, 2007, 2017-present)')
        expected_cut = [('Bass', [(1989, 2004), (2007, 2007), (2017, 'present')])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Guitars(1991-1993), Bass(1993)')
        expected_cut = [('Guitars', [(1991, 1993)]),
                        ('Bass', [(1993, 1993)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Bass (1989-2004, 2017-present), Flute, Triangle (1989-2004)')
        expected_cut = [('Bass', [(1989, 2004), (2017, 'present')]),
                        ('Flute, Triangle', [(1989, 2004)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments(
            'Drums, Vocals (additional)(1970, 1972-1973, 1987-present), Bass, Guitars (additional)(1993-present)')
        expected_cut = [('Drums, Vocals (additional)', [(1970, 1970), (1972, 1973), (1987, 'present')]),
                        ('Bass, Guitars (additional)', [(1993, 'present')])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Bass (on EP 1)')
        expected_cut = [('Bass', [])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Bass (5-string) (1997-present)')
        expected_cut = [('Bass', [(1997, 'present')])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Bass (10-string) (1997-present)')
        expected_cut = [('Bass', [(1997, 'present')])]
        self.assertEqual(expected_cut, result)

    def test_question_marks(self):
        result = cut_instruments('Drums	(?-2011)')
        expected_cut = [('Drums', [('?', 2011)])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Drums	(2011-?)')
        expected_cut = [('Drums', [(2011, '?')])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Drums	(2007-2009, 2011-?)')
        expected_cut = [('Drums', [(2007, 2009), (2011, '?')])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Drums	(2007-2009, ?-present)')
        expected_cut = [('Drums', [(2007, 2009), ('?', 'present')])]
        self.assertEqual(expected_cut, result)

        result = cut_instruments('Guitars (, 2018-?)')
        expected_cut = [('Guitars', [(2018, '?')])]
        self.assertEqual(expected_cut, result)
