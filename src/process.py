#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd


def normalise(d, which=-1):
    if (type(d) == pd.core.frame.DataFrame):
        d = d.apply(lambda x: x / x[which], 1)
    elif (type(d) == np.ndarray):
        d = np.divide(d.T, d.T[which, :]).T
    else:
        raise TypeError("Supply DataFrame or NumPy array")
    return np.array(d)


def stack(d):
    return np.divide(np.sum(d, axis=0), d.shape[0])
    # return np.sum(d, axis=0)/d.shape[0]


def bin(d, by, bins, transform=None):
    vs = transform(d[by]) if transform is not None else d[by]
    return np.digitize(vs, bins)


def count_grouped(d):
    d = np.sort(d)
    dif = np.concatenate(([1], np.diff(d)))
    idx = np.concatenate((np.where(dif)[0], [d.shape[0]]))
    grouped = np.empty(len(idx)-1,\
     dtype=np.dtype([('value',np.int32), ('count',np.int32)]))
    grouped['value'] = d[idx[:-1]]
    grouped['count'] = np.diff(idx)
    return grouped
