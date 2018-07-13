#!/usr/bin/env python3
import logging
import sys

import defopt
import numpy as np
import pandas as pd

from hbtp import HBTReader
from src import read


def bin(data, by, nbins):
    return pd.cut(
        data[by],
        np.linspace(data[by].min(), data[by].max(), nbins + 1),
        retbins=False,
        labels=np.arange(1, nbins + 1),
    )


def main(grav, snap):
    """Split halo IDS into 2 groups, below and above percentile range in log10(D_Nf).

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 9)
    """
    logging.info("Loading snapshot %d of run %s" % (snap, grav))

    reader = HBTReader("./data/%s/subcat/" % grav)
    ids = read.ids(grav, snap)
    haloes = reader.LoadHostHalos(snap)[ids]

    data = pd.read_csv("./output/dnf.%s.%03d.csv" % (grav, snap)).set_index(
        "HostHaloId"
    )
    data["M200Crit"] = np.log10(1e10 * haloes["M200Crit"])
    data["D_Nf"] = np.log10(data["D_Nf"])
    data["bin_log10_m200"] = bin(data, "M200Crit", 20)

    dnf_quantiles = data.groupby("bin_log10_m200").quantile([.25, .75])["D_Nf"]
    dnf_quantiles = dnf_quantiles.iloc[0:-2]  # remove most massive halo
    dnf_quantiles = dnf_quantiles[~dnf_quantiles.isna()]  # remove nans

    open("./output/ids_under.%s.%03d.csv" % (grav, snap), "w").close()
    open("./output/ids_over.%s.%03d.csv" % (grav, snap), "w").close()
    for b in np.unique(data["bin_log10_m200"]):
        if b in dnf_quantiles.index:
            under, over = (
                dnf_quantiles.loc[b].values[0],
                dnf_quantiles.loc[b].values[-1],
            )
            f_under, f_over = (
                open("./output/ids_under.%s.%03d.csv" % (grav, snap), "a"),
                open("./output/ids_over.%s.%03d.csv" % (grav, snap), "a"),
            )
            np.savetxt(
                f_under,
                data[
                    (data["bin_log10_m200"] == b) & (data["D_Nf"] <= under)
                ].index.values,
                fmt="%d",
            )
            np.savetxt(
                f_over,
                data[
                    (data["bin_log10_m200"] == b) & (data["D_Nf"] > over)
                ].index.values,
                fmt="%d",
            )
            f_under.close()
            f_over.close()

    # sys.stdout.write("bin_log10_m200,percentile,D_Nf\n")
    # dnf_quantiles.to_csv(sys.stdout)


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
