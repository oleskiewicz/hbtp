#!/usr/bin/env python3
import logging
import sys

import defopt
import numpy as np
import pandas as pd

from hbtp import HBTReader
from src import read


class HBTEnvironmentReader(HBTReader):
    """Extends HBTReader with environment calculations.
    """

    def __init__(self, subhalo_path):
        HBTReader.__init__(self, subhalo_path)

    def ConditionalNearestNeighbour(self, isnap, ids, f=1.0, N=0):
        """N-th neighbour more massive than f*M.

        .. todo::

            Error handling for small numbers of haloes
        """

        def __d(halo, f=1.0, N=0):
            _haloes = haloes[
                (haloes["HaloId"] != halo["HaloId"])
                & (haloes["M200Crit"] >= 1.0 * halo["M200Crit"])
            ]

            if len(_haloes) < 1:
                d = np.inf

            else:
                _ds = np.linalg.norm(
                    _haloes["CenterComoving"] - halo["CenterComoving"], axis=1
                )

                _neighbour_index = _ds.argsort()[N]

                d = (
                    _ds[_neighbour_index]
                    / _haloes[_neighbour_index]["R200CritComoving"]
                )

            return d

        logging.info("Querying %d haloes" % len(ids))
        haloes = self.LoadHostHalos(isnap)[ids]
        return [__d(x) for x in haloes]


def main(grav, snap):
    """Calculate halo environmental properties.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    """
    ids = read.ids(grav, snap)
    reader = HBTEnvironmentReader("./data/%s/subcat" % grav)
    logging.info("%d haloes at snapshot %d" % (len(ids), snap))

    pd.DataFrame(
        {"D_Nf": reader.ConditionalNearestNeighbour(snap, ids)}, index=ids
    ).to_csv(sys.stdout, index=True, index_label="HostHaloId")


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
