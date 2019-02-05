#!/usr/bin/env python3
import logging
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.stats import bayesian_blocks
from scipy.optimize import curve_fit

import cosmology
from hbtp import HBTReader
from src import read

logging.basicConfig(level=logging.INFO)


def mf(haloes, edges):
    """Bins FoF haloes
    """

    if edges == "bayes":
        edges = bayesian_blocks(haloes["M200Crit"])

    try:
        counts, edges = np.histogram(haloes["M200Crit"], edges)
    except ValueError:
        logging.exception("Error binning haloes")
        sys.exit(1)

    centres = 0.5 * (edges[1:] + edges[:-1])

    haloes = np.lib.recfunctions.append_fields(
        haloes,
        "bin",
        np.digitize(haloes["M200Crit"], edges, right=True),
        dtypes=[int],
        usemask=False,
    )

    return haloes, centres, counts


def prof(haloes):
    """Fits binned particle profiles for FoF haloes
    """
    ps = np.array(haloes["Profile"], dtype=np.float)
    xmin = 0.5 * np.cbrt((4.0 * np.pi) / (3.0 * np.sum(np.median(ps, axis=0))))
    xmax = 0.8
    x = np.linspace(-2.0, 0.0, 20)
    idx = np.where((np.power(10, x) < xmax) & (np.power(10, x) > xmin))

    ps = np.divide(ps.T, np.sum(ps, axis=1)).T
    p = np.median(ps, axis=0)

    def f(x, c):
        return np.log10(cosmology.nfw.m(np.power(10.0, x), c))

    c = curve_fit(
        f, x[idx], np.log10(np.median(np.cumsum(ps, axis=1), axis=0))[idx]
    )[0][0]

    return (
        c,
        idx,
        x,
        np.log10(np.median(np.cumsum(ps, axis=1), axis=0)),
        np.log10(cosmology.nfw.m_diff(np.power(10.0, x), c)),
        np.log10(p),
    )


def cmh(haloes, grav, snap, f=0.02, F=0.1):
    """Reads, calculates formation time of & plots CMHs of FoF haloes
    """
    ms = np.array(
        read.cmh(grav, snap, f).loc[haloes["HaloId"]].dropna(), dtype=np.float
    )
    ms = np.divide(ms.T, ms[:, -1]).T
    m = np.median(ms, axis=0)

    zs = read.snaps()
    z0 = zs[zs["Snapshot"] == snap][0]["Redshift"]
    rho = cosmology.rho_c(
        np.array(
            [
                zs[zs["Snapshot"] == s][0]["Redshift"]
                for s in np.arange(1 + snap - ms.shape[1], 1 + snap)
            ]
        )
    ) / cosmology.rho_c(z0)

    m_f = F * m[-1]
    y1, y2 = m[m > m_f][0], m[m < m_f][-1]
    x1, x2 = rho[m > m_f][0], rho[m < m_f][-1]
    rho_f = (np.log10(x1 / x2) / np.log10(y1 / y2)) * (
        np.log10(m_f / y1)
    ) + np.log10(x1)

    return np.log10(rho), np.log10(m), rho_f, np.log10(m_f), np.log10(ms)


def process(haloes, grav, snap, f, rs_f, bin, plot=False):
    # zs = read.snaps()
    # z0 = zs[zs["Snapshot"] == snap][0]["Redshift"]

    logging.debug("Snapshot %d, bin %d, %d haloes" % (snap, bin, len(haloes)))

    if plot:
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=[11, 5])

    rho_s = np.nan
    rho_f = np.nan

    try:
        c, _, _, _, _, _ = prof(haloes)
        rho_s = np.log10(cosmology.nfw.rho_enc(rs_f / c, c))
        F = cosmology.nfw.m(rs_f / c, c)
        try:
            _, _, rho_f, _, _ = cmh(haloes, grav, snap, f, F)
        except Exception as e:
            logging.error(
                "rho_f (run: %s, snapshot: %d, f: %.2f, bin: %d, haloes: %d): %s"
                % (grav, snap, f, bin, len(haloes), e)
            )
    except Exception as e:
        logging.error(
            "rho_s (run: %s, snapshot: %d, f: %.2f, bin: %d, haloes: %d): %s"
            % (grav, snap, f, bin, len(haloes), e)
        )

    if plot:
        fig.tight_layout()
        fig.savefig(
            "./plots/fig_%s.%03d.%03d.f%02d.rsf%02d.pdf"
            % (grav, snap, int(100 * f), bin, int(10 * rs_f))
        )

    return rho_f, rho_s


def concentration_mass(reader, grav, snap, f, nbins):
    """Plots concentration mass relation at a given snapshot
    """
    haloes, ms, _ = mf(reader, snap, nbins)
    cs = np.log10(
        [
            prof(haloes[haloes["bin"] == i + 1])[0]
            if len(haloes[haloes["bin"] == i + 1]) > 0
            else np.nan
            for i, m in enumerate(ms)
        ]
    )
    return ms, cs


if __name__ == "__main__":
    nbins = 20

    sys.stdout.write("prof,rs_f,grav,snap,f,bin,counts,rho_f,rho_s\n")
    for grav in ["GR_b64n512", "fr6_b64n512"]:
        reader = HBTReader("./data/%s/subcat" % grav)
        for snap in [122, 93, 78, 61, 51]:
            rs_f, f = 1.0, 0.02
            # for rs_f in [0.3, 1.0, 2.0]:
            #     for f in [0.01, 0.02, 0.1]:

            ids = read.ids(grav, snap, "ids")

            haloes = reader.LoadHostHalos(snap)
            haloes = haloes[ids]
            haloes["M200Crit"] = np.log10(1e10 * haloes["M200Crit"])

            haloes, _, counts = mf(haloes, nbins)
            for i, count in enumerate(counts):
                rho_f, rho_s = process(
                    haloes[haloes["bin"] == i + 1], grav, snap, f, rs_f, i + 1
                )
                sys.stdout.write(
                    "%s,%.2f,%s,%d,%.2f,%d,%d,%f,%f\n"
                    % ("nfw", rs_f, grav, snap, f, i + 1, count, rho_f, rho_s)
                )
