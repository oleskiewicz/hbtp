#!/usr/bin/env python
import sys
import logging
import numpy as np
from numpy.lib.recfunctions import append_fields

from .. import util
from HBTReader import HBTReader

if __name__ == '__main__':
    snap0 = int(sys.argv[1])
    host0 = int(sys.argv[2])
    reader = HBTReader("./data/")

    logging.info("Halo %d at snapshot %d" % (host0, snap0))

    # Dot merger tree
    with open("./output/mt_%03d_%d.dot" % (snap0, host0), 'w') as f:
        f.write("digraph {\n")
        t = reader.GetMergerTree(host0, snap0, f)
        f.write("}\n")
