#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

from HBTReader import HBTReader

if __name__ == '__main__':
	snap = int(sys.argv[1])
	nbins = 33
	bins = np.logspace(-2.5, 0.0, nbins)
	reader = HBTReader("./data/")

	with open("./output/hbtp/ids_%03d.txt"%snap, 'r') as f:
		hosts = map(lambda id: int(id.strip()), f.readlines())

	profs = pd.DataFrame(map(lambda h: reader.GetHostProfile(h, snap, bins=bins)[0],\
		hosts), columns=np.arange(1,nbins), index=hosts)
	profs.to_csv("./output/hbtp/prof_%03d.csv"%snap, sep=",", index_label="id")


