import numpy as np
import matplotlib.pyplot as plt
from lib.config.ConfigParser import ConfigParser
import sounddevice as sd
from lib.processing.Processor import Processor
from lib.model.generate import *
import matplotlib as mpl
import re
from copy import deepcopy
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
import threading
import queue
import re
from copy import deepcopy
from typing import List, Tuple, Optional

mpl.use('qtagg')
mpl.rcParams["path.simplify"] = True
mpl.rcParams["path.simplify_threshold"] = 1
plt.ion()

