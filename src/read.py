#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd


def snaps():
    d = np.genfromtxt("./output/redshift_list.txt", delimiter=" ",\
     dtype=np.dtype([('Snapshot', np.int32), ('Redshift', np.float32)]))
    return d


def prof(snap):
    d = pd.read_csv("./output/prof-%03d.csv" % snap)
    d.set_index('HaloId', inplace=True)
    d.fillna(0.0, inplace=True)
    return d


def cmh(snap):
    d = pd.read_csv("./output/cmh-%03d.csv" % snap)
    d.set_index('HaloId', inplace=True)
    d.fillna(0.0, inplace=True)
    return d


def ids(snap):
    with open("./output/ids-%03d.txt" % snap, 'r') as f:
        ids = map(lambda id: int(id.strip()), f.readlines())
    return ids
