#!/usr/bin/env python
import logging
import sys

import defopt
import numpy as np
from HBTReader import HBTReader


def main(grav, snap, host):
    """Construct & output merger tree

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param int host: Host halo ID
    """
    reader = HBTReader("./data/%s/subcat" % grav)

    logging.info("Halo %d at snapshot %d of %s" % (host, snap, grav))

    print("graph {")
    _ = reader.GetHostMergerTree(host, snap, sys.stdout)
    print("}")


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
