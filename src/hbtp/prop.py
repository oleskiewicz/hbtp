#!/usr/bin/env python
import sys

from HBTReader import HBTReader

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

if __name__ == '__main__':
	snap = int(sys.argv[1])
	reader = HBTReader("./data/")

	with open("./output/hbtp/ids_%03d.txt"%snap, 'r') as f:
		hosts = map(lambda id: int(id.strip()), f.readlines())

	with open("./output/hbtp/prop_%03d.csv"%snap, 'w') as f:
		f.write("snap,HaloId,R200CritComoving,M200Crit\n")
		for host_id in hosts:
			host = reader.GetHostHalo(host_id, snap)
			f.write("%d,%d,%f,%f\n"%(snap, host['HaloId'],\
				host['R200CritComoving'], host['M200Crit']))

