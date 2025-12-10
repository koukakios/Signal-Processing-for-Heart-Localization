import unittest
import numpy as np
import matplotlib
matplotlib.use("Agg")
from src.module_1.p3_downsampling import *

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
        assignment431()
        assignment432(config)