#!/usr/bin/env python
import sys
import logging
import numpy as np

from HBTReader import HBTReader

if __name__ == '__main__':
    snap = int(sys.argv[1])
    with open("./output/ids-%03d.txt" % snap, 'r') as f:
        ids = map(lambda id: int(id.strip()), f.readlines())
    logging.info("%d haloes at snapshot %d" % (len(ids), snap))

    reader = HBTReader("./data/")
    hosts = reader.LoadHostHalos(snap)[ids]
    columns = ['HaloId', 'R200CritComoving', 'M200Crit']

    np.savetxt("./output/prop-%03d.csv"%(snap),\
     hosts[columns], fmt="%d,%f,%f",\
     header=",".join(columns), comments="")
