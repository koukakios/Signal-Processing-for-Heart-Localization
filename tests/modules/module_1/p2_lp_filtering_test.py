import unittest
from unittest.mock import patch
import numpy as np
from src.module_1.p2_lp_filtering import *
import matplotlib.pyplot as plt

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
        assignment422(config)
        assignment423(config)
