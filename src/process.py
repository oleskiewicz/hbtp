#!/usr/bin/env python
import sys
import logging
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
# import matplotlib.pyplot as plt

from src.HBTReader import HBTReader
from src import read
from src import cosmology
from src import nfw

# from src import einasto


def mf(reader, snap, nbins):
    """Selects, bins & bins FoF haloes into log-spaced bins
    """
    hs = reader.LoadHostHalos(snap)
    # hs = hs[(hs['M200Crit'] >= 20) & (hs['CenterOffset'] >= 0.1)]
    hs = hs[hs['M200Crit'] >= 20]
    hs['M200Crit'] = 1e10 * hs['M200Crit']

    counts, bin_edges = np.histogram(np.log10(hs['M200Crit']), nbins)
    hs = np.lib.recfunctions.append_fields(
        hs,
        'bin',
        np.digitize(np.log10(hs['M200Crit']), bin_edges),
        usemask=False)
    bins = 0.5 * (bin_edges[1:] + bin_edges[:-1])

    return hs, bins, counts


def smf(reader, snap, ax=None):
    """Selects, bins & bins subhaloes into 20 log-spaced bins
    """
    subhaloes = reader.LoadSubhalos(snap)
    subhaloes = subhaloes[(subhaloes['HostHaloId'] != -1)
                          & (subhaloes['BoundM200Crit'] > 0.0) &
                          (subhaloes['Nbound'] >= 20)]

    counts, bin_edges = np.histogram(np.log10(subhaloes['BoundM200Crit']), 20)
    subhaloes = np.lib.recfunctions.append_fields(
        subhaloes,
        'bin',
        np.digitize(np.log10(subhaloes['BoundM200Crit']), bin_edges),
        usemask=False)
    bins = 0.5 * (bin_edges[1:] + bin_edges[:-1])

    if ax is not None:
        ax.plot(bins, np.log10(counts), marker='.')

    return subhaloes, counts, bins


def prof(haloes):
    """Reads, fits & plots binned particle profiles for FoF haloes
    """
    ps = np.array(haloes['Profile'], dtype=np.float)
    xmin = 0.5 * np.cbrt((4.0 * np.pi) / (3.0 * np.sum(np.median(ps, axis=0))))
    xmax = 0.8
    x = np.linspace(-2.0, 0.0, 20)
    idx = np.where((np.power(10, x) < xmax) & (np.power(10, x) > xmin))

    ps = np.divide(ps.T, np.sum(ps, axis=1)).T
    p = np.median(ps, axis=0)

    def f(x, c):
        return np.log10(nfw.m(np.power(10.0, x), c))

    c = curve_fit(
        f,
        x[idx],
        np.log10(np.median(np.cumsum(ps, axis=1), axis=0))[idx],
    )[0][0]

    return c, idx, x, np.log10(np.median(np.cumsum(ps, axis=1), axis=0)),\
     np.log10(nfw.m_diff(np.power(10.0, x), c)), np.log10(p)


def cmh(grav, snap, haloes, F=0.1):
    """Reads, calculates formation time of & plots CMHs of FoF haloes
    """
    ms = np.array(
        read.cmh(grav, snap).loc[haloes['HaloId']].dropna(), dtype=np.float)
    ms = np.divide(ms.T, ms[:, -1]).T
    m = np.median(ms, axis=0)

    zs = read.snaps()
    z0 = zs[zs['Snapshot'] == snap][0]['Redshift']
    rho = cosmology.rho_c(
     np.array([zs[zs['Snapshot'] == s][0]['Redshift']
     for s in np.arange(1+snap-ms.shape[1], 1+snap)])) / \
     cosmology.rho_c(z0)

    m_f = F * m[-1]
    y1, y2 = m[m > m_f][0], m[m < m_f][-1]
    x1, x2 = rho[m > m_f][0], rho[m < m_f][-1]
    rho_f = (np.log10(x1 / x2) / np.log10(y1 / y2)) * \
     (np.log10(m_f / y1)) + np.log10(x1)

    return np.log10(rho), np.log10(m), rho_f, np.log10(m_f), np.log10(ms)


def process(grav, snap, hs, bin):
    zs = read.snaps()
    z0 = zs[zs['Snapshot'] == snap][0]['Redshift']

    hs = hs[hs['bin'] == bin]

    logging.info('Snapshot %d, bin %d, %d haloes' % (snap, bin, len(hs)))

    rho_f = np.nan
    rho_s = np.nan

    try:
        c, _, _, _, _, _ = prof(hs)
        rho_s = np.log10(nfw.rho_enc(1.0 / c, c))
        F = nfw.m(1.0 / c, c)
        try:
            _, _, rho_f, _, _ = cmh(grav, snap, hs, F)
        except:
            logging.error(
                'Formation time (snapshot: %d, bin: %d, haloes: %d)' %
                (snap, bin, len(hs)))
    except:
        logging.error('Density profile (snapshot: %d, bin: %d, haloes: %d)' %
                      (snap, bin, len(hs)))

    return rho_s, rho_f


def concentration_mass(reader, grav, snap, nbins):
    """Plots concentration mass relation at a given snapshot
    """
    hs, _, m = mf(reader, snap, nbins)
    c = np.log10([process(grav, snap, hs, bin) for bin in range(1, nbins + 1)])
    m = m[c != -1.0]
    c = c[c != -1.0]

    return m, c


if __name__ == '__main__':
    nbins = 10

    # snap = 122  #int(sys.argv[1])
    # grav = "GR_b64n512"  #sys.argv[1]
    # r = HBTReader("./data/%s/subcat" % grav)
    # bin = 10

    # m, c = concentration_mass(r, snap, nbins)

    # hs, bins, counts = mf(r, snap, nbins)

    # c, _, _, _, _, _ = prof(hs[hs['bin'] == bin])

    # x, y_med, x_fit, y_fit, ys = cmh(snap, hs[hs['bin'] == bin], 0.1)

    print('grav,snap,bin,counts,rho_f,rho_s')
    for grav in ["GR_b64n512", "fr6_b64n512"]:
        r = HBTReader("./data/%s/subcat" % grav)
        for snap in [122, 93, 78, 61]:
            hs, _, counts = mf(r, snap, nbins)
            for bin in range(1, nbins + 1):
                # try:
                rho_f, rho_s = process(grav, snap, hs, bin)
                print('%s,%d,%d,%d,%f,%f' % (grav, snap, bin, counts[bin - 1],
                                             rho_f, rho_s))
                # except:
                #     logging.error('Failed snapshot %d, bin %d'%(snap, bin))
