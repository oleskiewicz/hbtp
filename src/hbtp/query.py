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

	log.info("Loading snapshot %d"%(snap))

	hosts = reader.LoadHostHalos(snap)[['HaloId','R200CritComoving','M200Crit']]

	# filter small mass haloes
	hosts = hosts[hosts['M200Crit'] >= 20]
	# ids = hosts['HaloId']

	# filter orphan hosts
	ids = list(filter(lambda id: len(reader.GetSubsOfHost(id,snap)) > 0,\
		hosts['HaloId']))

	log.info("Found %d haloes"%(len(ids)))

	with open("./output/hbtp/ids-%03d.txt"%snap, 'w') as f:
		for id in ids:
			f.write("%d\n"%id)
