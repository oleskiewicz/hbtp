#!/usr/bin/env python3
import logging
import sys

import defopt

from hbtp import HBTReader


def main(grav, snap, verbose=True):
    """Query & filter halo IDs.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 9)
    :param bool verbose: print to stdout?
    """
    logging.info("Loading snapshot %d of run %s" % (snap, grav))

    reader = HBTReader("./data/%s/subcat" % grav)
    hosts = reader.LoadHostHalos(snap)

    # FILTER 1: small mass haloes
    hosts = hosts[hosts["M200Crit"] >= 20]

    # # FILTER 2: CenterOffset
    # hosts = hosts[hosts["CenterOffset"] >= 0.07]

    # # FILTER 3: orphan hosts - redundant
    # hosts = [host for host in hosts if len(reader.GetSubsOfHost(host["HaloId"], snap)) > 0]

    ids = hosts["HaloId"]

    logging.info("Found %d haloes" % (len(ids)))

    if verbose:
        for i in ids:
            sys.stdout.write("%d\n" % i)

    return ids


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
