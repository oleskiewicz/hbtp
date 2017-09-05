#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd

def normalise(d, which = -1):
  if (type(d) == pd.core.frame.DataFrame):
    d = d.apply(lambda x: x/x[which], 1)
  elif (type(d) == np.ndarray):
    d = np.divide(d.T, d.T[which,:]).T
  else:
    raise TypeError("Supply DataFrame or NumPy array")
  return np.array(d)

def stack(d):
  return np.sum(d, axis=0)/d.shape[0]
