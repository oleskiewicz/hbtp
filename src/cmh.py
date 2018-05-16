#!/usr/bin/env python
import sys
import logging
import numpy as np
import pandas as pd
from numpy.lib.recfunctions import append_fields
import defopt

from HBTReader import HBTReader


class HBTHistoryReader(HBTReader):
    """Extends HBTReader with CMH options.
    """

    def __init__(self, subhalo_path):
        HBTReader.__init__(self, subhalo_path)

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

        m0 = self.GetHostHalo(HostHaloId, isnap)['M200Crit']
        trackIds = self.GetSubsOfHost(HostHaloId, isnap)['TrackId']

        logging.info(
            "Starting halo %d of mass %.2f with %d tracks at snapshot %d" %
            (HostHaloId, m0, len(trackIds), isnap))

        hosts = []
        for trackId in trackIds:
            hosts.extend(
                self.GetTrack(trackId,
                              MaxSnap=isnap)[["Snapshot", "HostHaloId"]])

        hosts = np.unique(np.array(hosts), axis=0)
        # hosts = hosts[hosts['HostHaloId'] != 0]

        masses = [
            self.GetHostHalo(host['HostHaloId'], host['Snapshot'])['M200Crit']
            for host in hosts
        ]
        hosts = append_fields(hosts, 'M200Crit', masses, usemask=False)
        snaps = np.unique(hosts['Snapshot'])

        logging.debug(
            "Queried halo %d@%d with %d host halos across %d snapshots" %
            (HostHaloId, isnap, len(hosts), len(snaps)))

        cmh = np.array(
            zip(np.full_like(snaps, HostHaloId), snaps, np.zeros_like(snaps)),
            dtype=np.dtype([
                ('HostHaloId', np.int32),
                ('Snapshot', np.int32),
                ('M200Crit', np.float32),
            ]))
        for i, _ in np.ndenumerate(cmh):
            cmh[i]['M200Crit'] = np.sum(filter(lambda m: m > f * m0,\
                hosts[hosts['Snapshot'] == cmh[i]['Snapshot']]['M200Crit']))

        logging.info("Finished CMH for halo %d@%d" % (HostHaloId, isnap))

        return cmh


def pad(ls, value=0.0, on_left=True):
    """Pad a 2D list with values.

    Converts this::

        [[1, 2, 3],
         [2, 3]]

    Into this::

        [[1, 2, 3],
         [0, 2, 3]]

    :param list ls: list of lists
    :param float value: what to pad with
    :param bool on_left: pad on the left if True, on the Right if False
    """

    maxlen = max([len(l) for l in ls])
    for i, l in enumerate(ls):
        if len(ls[i]) < maxlen:
            if on_left:
                ls[i] = ([
                    value,
                ] * (maxlen - len(l))) + l
            else:
                ls[i] = l + ([
                    value,
                ] * (maxlen - len(l)))
    return maxlen, ls


def g(x):
    return x * x


def main(grav, snap, hosts, f=0.02):
    """Calculate & print CMH of a halo.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param list[int] hosts: host halo IDs
    :param float f: NFW f parameter
    """

    reader = HBTHistoryReader("./data/%s/subcat" % grav)
    # cmh = reader.GetCollapsedMassHistory(host, snap, f)

    nsnaps, cmhs = pad([
        list(reader.GetCollapsedMassHistory(host, snap, f)["M200Crit"])
        for host in hosts
    ])

    cmhs = pd.DataFrame(
        cmhs, index=hosts, columns=range(snap - nsnaps + 1, snap + 1))

    cmhs.to_csv(sys.stdout, index_label="HostHaloId")


if __name__ == '__main__':
    defopt.run(main, short={'f': 'f', 'hosts': 'H'}, strict_kwonly=False)
