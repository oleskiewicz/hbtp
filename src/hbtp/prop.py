#!/usr/bin/env python
import sys
import numpy as np

from HBTReader import HBTReader

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

if __name__ == '__main__':
	snap = int(sys.argv[1])
	with open("./output/ids-%03d.txt"%snap, 'r') as f:
		ids = map(lambda id: int(id.strip()), f.readlines())
	log.info("%d haloes at snapshot %d"%(len(ids),snap))

	reader = HBTReader("./data/")
	hosts = reader.LoadHostHalos(snap)[ids]
	columns = ['HaloId', 'R200CritComoving', 'M200Crit']

	np.savetxt("./output/prop-%03d.csv"%(snap),\
		hosts[columns], fmt="%d,%f,%f",\
		header=",".join(columns), comments="")
