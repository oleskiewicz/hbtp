#!/usr/bin/env python3
import logging
import sys

import defopt
import numpy as np
import pandas as pd
from numpy.lib.recfunctions import append_fields

from hbtp import HBTReader

from .util import pmap

logging.basicConfig(level=logging.INFO)


class HBTHistoryReader(HBTReader):
    """Extends HBTReader with CMH options.
    """

    def __init__(self, subhalo_path):
        HBTReader.__init__(self, subhalo_path)

    def GetProgenitorHaloesRecursive(self, HostHaloId, isnap=-1, maxsnap=None):

        progs = set()

        def rec(s, i):
            if maxsnap is not None:
                if s < maxsnap:
                    return
            _progs = set(self.GetProgenitorHaloes(i, s))
            if len(_progs) == 0:
                return
            for p in _progs:
                progs.add((s - 1, p))
                rec(s - 1, p)

        rec(isnap, HostHaloId)

        return list(progs)

    def GetCollapsedMassHistory(self, HostHaloId, isnap=-1, f=0.02):
        """Calculates a CMH, starting at a FOF group.

        CMH is a sum of masses of all progenitors over a threshold.

        Arguments:
            HostHaloId (int): starting point of the tree
            isnap (int): (default = -1) initial snapshot
            f (float): (default = 0.02) NFW :math:`f` parameter

        Returns:
            (numpy.ndarray): CMH of a host halo
        """

        m0 = self.GetHostHalo(HostHaloId, isnap)["M200Crit"]
        trackIds = self.GetSubsOfHost(HostHaloId, isnap)["TrackId"]

        logging.info(
            "CMH for halo [%d] (mass = %.2f, %d tracks, snapshot = %d)"
            % (HostHaloId, m0, len(trackIds), isnap)
        )

        hosts = []
        for trackId in trackIds:
            hosts.extend(
                self.GetTrack(trackId, MaxSnap=isnap)[
                    ["Snapshot", "HostHaloId"]
                ]
            )

        hosts = np.unique(np.array(hosts), axis=0)
        # hosts = hosts[hosts['HostHaloId'] != 0]

        masses = [
            self.GetHostHalo(host["HostHaloId"], host["Snapshot"])["M200Crit"]
            for host in hosts
        ]
        hosts = append_fields(hosts, "M200Crit", masses, usemask=False)
        snaps = np.unique(hosts["Snapshot"])

        logging.debug(
            "Queried halo %d@%d with %d host(s) across %d snapshots"
            % (HostHaloId, isnap, len(hosts), len(snaps))
        )

        cmh = np.array(
            zip(np.full_like(snaps, HostHaloId), snaps, np.zeros_like(snaps)),
            dtype=np.dtype(
                [
                    ("HostHaloId", np.int32),
                    ("Snapshot", np.int32),
                    ("M200Crit", np.float32),
                ]
            ),
        )
        for i, _ in np.ndenumerate(cmh):
            cmh[i]["M200Crit"] = np.sum(
                filter(
                    lambda m: m > f * m0,
                    hosts[hosts["Snapshot"] == cmh[i]["Snapshot"]]["M200Crit"],
                )
            )

        logging.debug(
            "Finished CMH for halo %d at snapshot %d" % (HostHaloId, isnap)
        )

        return cmh


def main(grav, snap, hosts, f=0.02):
    """Calculate & print CMH of a halo.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param list[int] hosts: host halo IDs
    :param float f: NFW f parameter
    """

    pd.concat(
        pmap(
            lambda host: pd.DataFrame(
                HBTHistoryReader(
                    "./data/%s/subcat" % grav
                ).GetCollapsedMassHistory(host, snap, f)
            ),
            hosts,
        )
    ).pivot_table(
        values="M200Crit",
        columns="Snapshot",
        index="HostHaloId",
        fill_value=0.0,
    ).to_csv(
        sys.stdout, index=True, index_label="HostHaloId"
    )


if __name__ == "__main__":
    defopt.run(main, short={"f": "f", "hosts": "H"}, strict_kwonly=False)
