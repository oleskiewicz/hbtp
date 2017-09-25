#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

from HBTReader import HBTReader
from src import read

if __name__ == '__main__':
	snap = int(sys.argv[1])
	ids = read.ids(snap)
	log.info("%d haloes at snapshot %d"%(len(ids),snap))

	nbins = 32
	bins = np.concatenate(([0.0,], np.logspace(-2.5, 0.0, nbins)))
	reader = HBTReader("./data/")
	profs = pd.DataFrame(map(lambda id:\
		reader.GetHostProfile(id, snap, bins=bins)[0], ids),\
		columns=np.arange(0,nbins), index=ids)
	profs.to_csv("./output/hbtp/prof-%03d.csv"%snap,\
		sep=",", index_label="HaloId")
