#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd


def snaps():
    d = np.genfromtxt("./data/redshift_list.txt", delimiter=" ",\
     dtype=np.dtype([('Snapshot', np.int32), ('Redshift', np.float32)]))
    return d


def cmh(grav, snap, f=0.02):
    d = pd.read_csv("./output/cmh.f%03d.%s.%03d.csv" % (100 * f, grav, snap))
    d.set_index('HostHaloId', inplace=True)
    d.fillna(0.0, inplace=True)
    return d


def ids(grav, snap):
    with open("./output/ids.%s.%03d.csv" % (grav, snap), "r") as f:
        ids = list(map(lambda id: int(id.strip()), f.readlines()))
    return ids
