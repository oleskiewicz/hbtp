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

	log.debug("Snapshot %d"%(snap))

	hosts = filter(lambda h: len(reader.GetSubsOfHost(h, snap)) > 0,\
		reader.LoadHostHalos(isnap=snap)['HaloId'])

	log.debug("%d haloes"%(len(hosts)))

	with open("./output/hbtp/ids_%03d.txt"%snap, 'w') as f:
		for host in hosts:
			f.write("%d\n"%host)

