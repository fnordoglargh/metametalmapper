import unittest
from metal_crawler import cook_soup


# Executing this test case reports a "ResourceWarning: unclosed <ssl.SSLSocket [...]"
# See https://github.com/psf/requests/issues/3912:
# "You don't have to. The warning is just that: a warning. No error occurs when you see it, and it is not an indication
# of the program doing the wrong thing. It's entirely expected behaviour, and this is working as designed. However, if
# you're concerned about them, you may call close."
class MyTestCase(unittest.TestCase):

    def test_cooking(self):
        result = cook_soup('https://www.metal-archives.com/bands/Drakthrone/198421321541')
        self.assertEqual(result, None)

        result = cook_soup('https://www.metal-archives.com/artists/Fetnrirr/104166845133158')
        self.assertEqual(result, None)

        result = cook_soup('https://www.metal-archives.com/artists/Fenriz/104166845133158')
        self.assertEqual(result, None)

        result = cook_soup('https://www.blablacotour.fr')
        self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
