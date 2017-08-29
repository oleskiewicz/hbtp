#!/usr/bin/env python
import sys
import numpy as np
import logging
from logging.config import fileConfig

from HBTReader import HBTReader

if __name__ == '__main__':
	fileConfig("./logging.conf")
	log = logging.getLogger()

	snap = int(sys.argv[1])
	reader = HBTReader("./data/")

	hosts = filter(lambda h: len(reader.GetSubsOfHost(h, snap)) > 0,\
		reader.LoadHostHalos(isnap=snap)['HaloId'])
	with open("./output/hbtp/ids_%03d.txt"%snap, 'w') as f:
		for host in hosts:
			f.write("%d\n"%host)

