from unittest.mock import patch
import unittest
import numpy as np
import matplotlib.pyplot as plt

from src.module_1.p4_spectrogram_analysis import *

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
        assignment441(config)
