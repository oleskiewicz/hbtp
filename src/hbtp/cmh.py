#!/usr/bin/env python
import sys
from itertools import groupby
import fcntl

from .. import util
from HBTReader import HBTReader

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

if __name__ == '__main__':
	snap = int(sys.argv[1])
	host = int(sys.argv[2])
	f0 = 0.1
	reader = HBTReader("./data/")

	t = reader.GetMergerTree(host, snap)
	# # Dot merger tree
	# with open("./output/hbtp/mt_%03d_%d.dot"%(snap, host), 'w') as f:
	# 	f.write("digraph {\n")
	# 	t = reader.GetMergerTree(host, snap, f)
	# 	f.write("}\n")

	# CMH
	m0 = reader.GetHostHalo(host, snap)['M200Crit']
	m = {}
	for k,vs in groupby(map(lambda h: vars(h), util.flatten(t)), key=lambda h: h['isnap']):
		ms = sum(filter(lambda mass: mass > f0*m0, map(lambda h: h['M200Crit'], vs)))
		try:
			m[k] += ms
		except:
			m[k] = ms
	with open("./output/hbtp/cmh_%03d_%d.csv"%(snap,host), 'a') as f:
		# fcntl.flock(f, fcntl.LOCK_EX)
		for k in m:
			f.write("%d,%03d,%03d,%f\n"%(host, snap, k, m[k]))
		# fcntl.flock(f, fcntl.LOCK_UN)
