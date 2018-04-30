#!/usr/bin/env python
import sys
import logging
import numpy as np

from HBTReader import HBTReader

if __name__ == '__main__':
    snap = int(sys.argv[1])
    reader = HBTReader("./data/")

    logging.info("Loading snapshot %d" % (snap))

    hosts = reader.LoadHostHalos(snap)

    # small mass haloes & relaxed
    hosts = hosts[(hosts['M200Crit'] >= 20) & (hosts['CenterOffset'] >= 0.1)]
    ids = hosts['HaloId']

    # # filter orphan hosts - redundant
    # ids = list(filter(lambda id: len(reader.GetSubsOfHost(id,snap)) > 0,\
    # 	hosts['HaloId']))

    logging.info("Found %d haloes" % (len(ids)))

    with open("./output/ids-%03d.txt" % snap, 'w') as f:
        for id in ids:
            f.write("%d\n" % id)
