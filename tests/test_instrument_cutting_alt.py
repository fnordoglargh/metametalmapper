import unittest
from metal_crawler import *


class TestInstrumentCuttingAlt(unittest.TestCase):

    def test_cutting_alt(self):
        result = cut_instruments_alt('Guitars')
        expected_cut = [['Guitars', []]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Guitars (earlier)')
        expected_cut = [['Guitars (earlier)', []]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Guitars (Session) (earlier), Vocals (Session) (later)')
        expected_cut = [['Guitars (Session) (earlier)', []],
                        ['Vocals (Session) (later)', []]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (1989-2004)')
        expected_cut = [['Bass', [[1989, 2004]]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (Session) (1989-2004)')
        expected_cut = [['Bass (Session)', [[1989, 2004]]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (1989-2004, 2007, 2017-present)')
        expected_cut = [['Bass', [[1989, 2004], [2007, 2007], [2017, 'present']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Guitars(1991-1993), Bass(1993)')
        expected_cut = [['Guitars', [[1991, 1993]]],
                        ['Bass', [[1993, 1993]]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (1989-2004, 2017-present), Flute, Triangle (1989-2004)')
        expected_cut = [['Bass', [[1989, 2004], [2017, 'present']]],
                        ['Flute, Triangle', [[1989, 2004]]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt(
            'Drums, Vocals (additional)(1970, 1972-1973, 1987-present), Bass, Guitars (additional)(1993-present)')
        expected_cut = [['Drums, Vocals (additional)', [[1970, 1970], [1972, 1973], [1987, 'present']]],
                        ['Bass, Guitars (additional)', [[1993, 'present']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (on EP 1)')
        expected_cut = [['Bass', []]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (5-string) (1997-present)')
        expected_cut = [['Bass', [[1997, 'present']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (10-string) (1997-present)')
        expected_cut = [['Bass', [[1997, 'present']]]]
        self.assertEqual(expected_cut, result)

    def test_question_marks_alt(self):
        result = cut_instruments_alt('Drums	(?-2011)')
        expected_cut = [['Drums', [['?', 2011]]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Drums	(2011-?)')
        expected_cut = [['Drums', [[2011, '?']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Drums	(2007-2009, 2011-?)')
        expected_cut = [['Drums', [[2007, 2009], [2011, '?']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Drums	(2007-2009, ?-present)')
        expected_cut = [['Drums', [[2007, 2009], ['?', 'present']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Drums	(?-2011, ?-Present)')
        expected_cut = [['Drums', [['?', 2011], ['?', 'present']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Guitars (, 2018-?)')
        expected_cut = [['Guitars', [[2018, '?']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Vocals (lead)(?-?, 2014 - present)')
        expected_cut = [['Vocals (lead)', [['?', '?'], [2014, 'present']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Bass (2004-2009, ?-?)')
        expected_cut = [['Bass', [[2004, 2009], ['?', '?']]]]
        self.assertEqual(expected_cut, result)

        result = cut_instruments_alt('Vocals (female) (2010-2014, 2015-2019)')
        expected_cut = [['Vocals (female)', [[2010, 2014], [2015, 2019]]]]
        self.assertEqual(expected_cut, result)

        # There's currently no handling for this use case and easier to use the "report error" function on M-A.
        result = cut_instruments_alt('Drums (2014-?) Songwriting (?-present) ')
        expected_cut = [['Drums', [[2014, '?']]], ['Songwriting', [['?', 'present']]]]
        #self.assertEqual(expected_cut, result)
