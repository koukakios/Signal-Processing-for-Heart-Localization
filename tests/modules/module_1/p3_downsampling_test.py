from unittest.mock import patch
import unittest
import matplotlib.pyplot as plt
import numpy as np
from src.module_1.p3_downsampling import *

class TestCLI(unittest.TestCase):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    @patch("matplotlib.pyplot.show", lambda: None)  # replaces show with no-op
    def test_no_error(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        config = ConfigParser()
        assignment431()
        assignment432(config)
