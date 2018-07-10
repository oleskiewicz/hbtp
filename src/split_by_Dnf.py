#!/usr/bin/env python3
import logging
import sys

import defopt
import numpy as np
import pandas as pd

from hbtp import HBTReader


def bin(data, by, nbins):
    return pd.cut(
        data[by],
        np.linspace(data[by].min(), data[by].max(), nbins + 1),
        retbins=False,
        labels=np.arange(1, nbins + 1),
    )


def main(grav, snap):
    """Query & filter halo IDs.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 9)
    :param bool verbose: print to stdout?
    """
    logging.info("Loading snapshot %d of run %s" % (snap, grav))

    reader = HBTReader("./data/%s/subcat/" % grav)
    haloes = reader.LoadHostHalos(snap)[
        [
            int(l.strip())
            for l in open(
                "./output/ids.%s.%03d.csv" % (grav, snap), "r"
            ).readlines()
        ]
    ]
    data = pd.read_csv("./output/env.%s.%03d.csv" % (grav, snap)).set_index(
        "HostHaloId"
    )
    data["M200Crit"] = np.log10(1e10 * haloes["M200Crit"])
    data["D_Nf"] = np.log10(data["D_Nf"])
    data["bin"] = bin(data, "M200Crit", 10)
    dnf_quantiles = data.groupby("bin").quantile([.32, .68])["D_Nf"]

    sys.stdout.write("bin_log10_m200,percentile,D_Nf\n")
    dnf_quantiles.to_csv(sys.stdout)


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
