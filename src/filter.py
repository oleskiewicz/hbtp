#!/usr/bin/env python
import logging
import defopt
import numpy as np

from HBTReader import HBTReader


def main(grav, snap, save=True):
    """Query & filter halo IDs.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param bool save: save IDs to file?
    """
    logging.info("Loading snapshot %d of run %s" % (snap, grav))

    reader = HBTReader("./data/%s/subcat" % grav)
    hosts = reader.LoadHostHalos(snap)

    # FILTER 1: small mass haloes
    hosts = hosts[hosts['M200Crit'] >= 20]
    ids = hosts['HaloId']

    # # FILTER 2: orphan hosts - redundant
    # ids = list(filter(lambda id: len(reader.GetSubsOfHost(id,snap)) > 0,
    #  hosts['HaloId']))

    logging.info("Found %d haloes" % (len(ids)))

    if save:
        with open("./output/ids.%s.%03d.csv" % (grav, snap), 'w') as f:
            for i in ids:
                f.write("%d\n" % i)

    return ids


if __name__ == '__main__':
    defopt.run(main, strict_kwonly=False)
