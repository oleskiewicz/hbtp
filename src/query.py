#!/usr/bin/env python3
import logging
import sys

import defopt
import numpy as np

from hbtp import HBTReader


def main(grav, snap, min_part_num=1000):
    """Query & filter halo IDs.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 9)
    :param int min_part_num: Minimum number of particles
    """
    logging.info("Loading snapshot %d of run %s" % (snap, grav))

    reader = HBTReader("./data/%s/subcat" % grav)
    haloes = reader.LoadHostHalos(snap)

    # FILTER 1: halo mass cut
    haloes = haloes[1e10 * haloes["M200Crit"] >= min_part_num * 1.52315180e8]

    # FILTER 2: CenterOffset
    haloes = haloes[haloes["CenterOffset"] >= 0.07]

    # # FILTER 3: orphan haloes - redundant
    # haloes = [host for host in haloes if len(reader.GetSubsOfHost(host["HaloId"], snap)) > 0]

    ids = haloes["HaloId"]

    logging.info("Found %d haloes" % (len(ids)))

    for i in ids:
        sys.stdout.write("%d\n" % i)

    return ids


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
