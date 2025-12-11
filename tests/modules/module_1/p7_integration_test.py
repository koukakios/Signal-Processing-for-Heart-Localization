import unittest
from unittest.mock import patch
import numpy as np
import matplotlib.pyplot as plt

from src.module_1.p7_integration import *

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
        assignment471(config)
