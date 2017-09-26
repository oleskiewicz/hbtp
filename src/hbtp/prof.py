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
	reader = HBTReader("./data/")
	log.info("%d haloes at snapshot %d"%(len(ids),snap))

	nbins = 20
	profs = pd.DataFrame(reader.GetHostProfile((ids,), snap),
		columns=np.arange(0,nbins), index=ids)
	profs.to_csv("./output/hbtp/prof-%03d.csv"%snap,\
		sep=",", index_label="HaloId")
