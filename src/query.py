#!/usr/bin/env python3
import logging
import sys

import defopt
import numpy as np

from hbtp import HBTReader


def main(grav, snap, min=1000):
    """Query & filter halo IDs.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 9)
    :param int min: Minimum number of particles
    """
    logging.info("Loading snapshot %d of run %s" % (snap, grav))

    reader = HBTReader("./data/%s/subcat" % grav)
    hosts = reader.LoadHostHalos(snap)

    # FILTER 1: halo mass cut
    hosts = hosts[np.sum(hosts["Profile"], axis=1) >= min]

    # FILTER 2: CenterOffset
    hosts = hosts[hosts["CenterOffset"] >= 0.07]

    # # FILTER 3: orphan hosts - redundant
    # hosts = [host for host in hosts if len(reader.GetSubsOfHost(host["HaloId"], snap)) > 0]

    ids = hosts["HaloId"]

    logging.info("Found %d haloes" % (len(ids)))

    for i in ids:
        sys.stdout.write("%d\n" % i)

    return ids


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
