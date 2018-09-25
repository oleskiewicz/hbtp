#!/usr/bin/env python3
import numpy as np
import pandas as pd


def snaps():
    d = np.genfromtxt(
        "./data/redshift_list.txt",
        delimiter=" ",
        dtype=np.dtype([("Snapshot", np.int32), ("Redshift", np.float32)]),
    )
    return d


def cmh(grav, snap, f=0.02):
    d = pd.read_csv("./output/cmh.f%03d.%s.%03d.csv" % (100 * f, grav, snap))
    d.set_index("HostHaloId", inplace=True)
    d.fillna(0.0, inplace=True)
    return d


def ids(grav, snap, prefix="ids"):
    return pd.read_csv(
        "./output/%s.%s.%03d.csv" % (prefix, grav, snap),
        header=None,
        names=["HaloId"],
    ).values[:, 0]
