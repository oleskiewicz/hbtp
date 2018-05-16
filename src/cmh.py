#!/usr/bin/env python
import sys
import logging
import multiprocessing as mp
import numpy as np
import pandas as pd
from numpy.lib.recfunctions import append_fields
import defopt
from HBTReader import HBTReader

logging.getLogger().setLevel(logging.INFO)


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
            "Calculating CMH for halo %d of mass %.2f with %d track(s) at snapshot %d"
            % (HostHaloId, m0, len(trackIds), isnap))

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
            "Queried halo %d@%d with %d host(s) across %d snapshots" %
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

        logging.debug("Finished CMH for halo %d at snapshot %d" % (HostHaloId,
                                                                   isnap))

        return cmh


def pad(ls, value=0.0, on_left=True):
    """Pad a 2D list with values.

    Converts this::

        [[1, 2, 3],
         [2, 3]]

    Into this::

        [[1, 2, 3],
         [0, 2, 3]]

    Note:

        This is serving as a poor replacement for ``pivot`` in ``pandas``, only
        for prototyping.

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


def pmap(f, xs, nprocs=mp.cpu_count()):
    """Parallel map.

    As seen in: <https://stackoverflow.com/a/16071616>.
    """

    def fun(f, q_in, q_out):
        while True:
            i, x = q_in.get()
            if i is None:
                break
            q_out.put((i, f(x)))

    q_in = mp.Queue(1)
    q_out = mp.Queue()

    proc = [
        mp.Process(target=fun, args=(f, q_in, q_out)) for _ in xrange(nprocs)
    ]

    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(xs)]
    [q_in.put((None, None)) for _ in xrange(nprocs)]
    res = [q_out.get() for _ in xrange(len(sent))]

    [p.join() for p in proc]

    return [x for i, x in res]


def main(grav, snap, hosts, f=0.02):
    """Calculate & print CMH of a halo.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param list[int] hosts: host halo IDs
    :param float f: NFW f parameter
    """

    pd.concat(pmap(lambda host:
        pd.DataFrame(HBTHistoryReader("./data/%s/subcat" % grav)
                     .GetCollapsedMassHistory(host, snap, f)),
        hosts))\
        .pivot_table(values='M200Crit', columns='Snapshot', index='HostHaloId', fill_value=0.0)\
        .to_csv(sys.stdout, index=True, index_label='HostHaloId')


if __name__ == '__main__':
    defopt.run(main, short={'f': 'f', 'hosts': 'H'}, strict_kwonly=False)
