import unittest
import numpy as np

from lib.model.generate import repeat

class TestGenerate(unittest.TestCase):
    def test_set_repeat(self):
        h_filtered = [3,2,1,0,-1]
        t_filtered = [0,1,2]
        _, a = repeat(5, h_filtered, t_filtered, 1, 3)
        self.assertTrue(np.array_equal(a, [3,  2,  1,  3,  1,  1,  3,  1,  1,  3,  1,  1,  3,  1,  1,  0, -1]))