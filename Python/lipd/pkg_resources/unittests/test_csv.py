from pkg_resources.helpers.csvs import _is_numeric_data

import unittest

numerics =  [
    [10.0, "nan"],
    [10.0, 12.0]
]
non_numerics = [
    [7.0, 102.0],
    ['OS-54863', 'OS-54864']
]
only_str = [
    ["s", "d"],
    ["d", "e"]
]

class MyTest(unittest.TestCase):

    def test_numerics(self):
        self.assertTrue(_is_numeric_data(numerics))

    def test_mixed(self):
        self.assertFalse(_is_numeric_data(non_numerics))

    def test_strings(self):
        self.assertFalse(_is_numeric_data(only_str))


if __name__ == '__main__':
    unittest.main(verbosity=2)