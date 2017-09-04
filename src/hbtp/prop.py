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
	reader = HBTReader("./data/")

	with open("./output/hbtp/ids_%03d.txt"%snap, 'r') as f:
		ids = map(lambda id: int(id.strip()), f.readlines())

	log.info("%d haloes at snapshot %d"%(len(ids),snap))

	hosts = []
	for id in ids:
		host = reader.GetHostHalo(id, snap)
		log.debug("Found halo %d"%(id))
		hosts.append((host['HaloId'], snap,\
			 host['R200CritComoving'], host['M200Crit']))

	hosts = np.array(hosts,\
		dtype=np.dtype([\
			('HostHaloId',np.int32),\
			('IdentificationSnapshot',np.int32),\
			('R200CritComoving',np.float32),\
			('M200Crit',np.float32)\
	]))

	np.savetxt("./output/hbtp/prop_%03d.csv"%(snap),\
		hosts, fmt="%d,%d,%f,%f",\
		header=",".join(hosts.dtype.names), comments="")
