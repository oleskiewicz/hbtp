#!/usr/bin/env python
import sys
import defopt
import logging
import numpy as np
import pandas as pd

from HBTReader import HBTReader
import read


def main(grav, snap, verbose=True):
    """Read & save halo profiles.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param bool verbose: print IDs to stdout?
    """
    ids = read.ids(grav, snap)
    reader = HBTReader("./data/%s/subcat" % grav)
    logging.info("%d haloes at snapshot %d" % (len(ids), snap))

    nbins = 20
    profs = pd.DataFrame(
        reader.GetHostProfile((ids, ), snap),
        columns=np.arange(0, nbins),
        index=ids)

    if verbose:
        profs.to_csv(sys.stdout, sep=",", index_label="HaloId")

    return profs


if __name__ == '__main__':
    defopt.run(main, strict_kwonly=False)
