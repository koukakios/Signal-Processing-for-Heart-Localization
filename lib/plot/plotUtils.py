import numpy as np
from matplotlib import axes

def scatter_constant(x: list|set|np.ndarray, const: int|float, plot: axes.Axes, c: str|None = None, label: str|None = None, marker: str|None = None, scaleX: float = 1):
    if len(x)>0:
        x = np.array(list(x)).flatten()
        y = np.full(len(x), const)
        plot.scatter(x * scaleX, y, c=c, label=label, marker=marker)
        