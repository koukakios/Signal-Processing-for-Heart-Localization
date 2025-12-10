import unittest
import numpy as np
import matplotlib
matplotlib.use("Agg")
from src.module_1.p6_segmentation import *

class TestGenerate(unittest.TestCase):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    def test_no_error(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        config = ConfigParser()
        segmentation(config)
