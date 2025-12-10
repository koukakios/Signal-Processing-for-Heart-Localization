import unittest
import numpy as np

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
        assignment431(config)
        assignment432(config)
