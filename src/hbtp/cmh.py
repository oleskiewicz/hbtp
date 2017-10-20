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
	host = int(sys.argv[2])
	NFW_f = 0.02
	reader = HBTReader("./data/")

	cmh = reader.GetCollapsedMassHistory(host, snap, NFW_f)
	np.savetxt("./output/cmh-%03d_%d.csv"%(snap,host),\
		cmh, fmt="%d,%d,%f")
	log.info("Wrote CMH for halo %d@%d"%(host,snap))
