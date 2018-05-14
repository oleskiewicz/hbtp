#!/usr/bin/env python
import sys
import defopt
import logging
import numpy as np

from HBTReader import HBTReader


def main(grav, snap, host, f=0.02):
    """Calculate & print CMH of a halo

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param int host: host halo ID
    :param float f: NFW f parameter
    """
    reader = HBTReader("./data/%s/subcat" % grav)
    cmh = reader.GetCollapsedMassHistory(host, snap, f)
    np.savetxt(
        "./output/cmh.f%03d.%s.%03d.%d.txt" % (f * 100, grav, snap, host),
        cmh,
        fmt="%d,%d,%f")
    logging.info("Wrote CMH for halo %d at snapshot %d of %s simulation" %
                 (host, snap, grav))


if __name__ == '__main__':
    defopt.run(main, strict_kwonly=False)
