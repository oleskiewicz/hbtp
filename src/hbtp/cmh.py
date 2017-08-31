#!/usr/bin/env python
import sys
import numpy as np

from .. import util
from HBTReader import HBTReader

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

if __name__ == '__main__':
	snap = int(sys.argv[1])
	host = int(sys.argv[2])
	NFW_f = 0.02
	reader = HBTReader("./data/")

	log.info("Halo %d at %d"%(host, snap))
	cmh = reader.GetCollapsedMassHistory([host,], snap, NFW_f)

	# CSV CMH
	with open("./output/hbtp/cmh_%03d_%d.csv"%(snap,host), 'w') as f:
		# fcntl.flock(f, fcntl.LOCK_EX)
		f.write("HaloId,IdentificationSnapshot,Snapshot,M200\n")
		for i,ms in enumerate(cmh):
			f.write("%d,%d,%d,%f\n"%(host,snap,snap-i,ms))
		# fcntl.flock(f, fcntl.LOCK_UN)

	# # Dot merger tree
	# with open("./output/hbtp/mt_%03d_%d.dot"%(snap, host), 'w') as f:
	# 	f.write("digraph {\n")
	# 	t = reader.GetMergerTree(host, snap, f)
	# 	f.write("}\n")
