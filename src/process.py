#!/usr/bin/env python3
import logging
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from hbtp import HBTReader
from src import cosmology, nfw, read

logging.basicConfig(level=logging.INFO)


def mf(reader, grav, snap, nbins):
    """Selects, filters & bins FoF haloes into log-spaced bins
    """
    haloes = reader.LoadHostHalos(snap)
    haloes = haloes[read.ids(grav, snap)]
    haloes["M200Crit"] = 1e10 * haloes["M200Crit"]
    logging.info("Found %d haloes" % len(haloes))

    bins = pd.cut(
        np.log10(haloes["M200Crit"]),
        np.linspace(
            np.log10(haloes["M200Crit"]).min(),
            np.log10(haloes["M200Crit"]).max(),
            nbins + 1,
        ),
        retbins=False,
        labels=np.arange(1, nbins + 1),
    )

    haloes = np.lib.recfunctions.append_fields(
        haloes, "bin", bins, dtypes=[int], usemask=False
    )

    counts = (
        pd.DataFrame(haloes[["HaloId", "bin"]])
        .groupby("bin")
        .count()
        .loc[np.arange(1, nbins + 1)]
        .values[:, 0]
    )
    counts[np.isnan(counts)] = -1.0
    counts = counts.astype(int)

    return haloes, bins, counts


def smf(reader, snap):
    """Selects, bins & bins subhaloes into 20 log-spaced bins
    """
    subhaloes = reader.LoadSubhalos(snap)
    subhaloes = subhaloes[
        (subhaloes["HostHaloId"] != -1)
        & (subhaloes["BoundM200Crit"] > 0.0)
        & (subhaloes["Nbound"] >= 20)
    ]

    counts, bin_edges = np.histogram(np.log10(subhaloes["BoundM200Crit"]), 20)
    subhaloes = np.lib.recfunctions.append_fields(
        subhaloes,
        "bin",
        np.digitize(np.log10(subhaloes["BoundM200Crit"]), bin_edges),
        usemask=False,
    )
    bins = 0.5 * (bin_edges[1:] + bin_edges[:-1])

    return subhaloes, counts, bins


def prof(haloes, ax=None):
    """Reads, fits & plots binned particle profiles for FoF haloes
    """
    ps = np.array(haloes["Profile"], dtype=np.float)
    xmin = 0.5 * np.cbrt((4.0 * np.pi) / (3.0 * np.sum(np.median(ps, axis=0))))
    xmax = 0.8
    x = np.linspace(-2.0, 0.0, 20)
    idx = np.where((np.power(10, x) < xmax) & (np.power(10, x) > xmin))

    ps = np.divide(ps.T, np.sum(ps, axis=1)).T
    p = np.median(ps, axis=0)

    def f(x, c):
        return np.log10(nfw.m(np.power(10.0, x), c))

    c = curve_fit(
        f, x[idx], np.log10(np.median(np.cumsum(ps, axis=1), axis=0))[idx]
    )[0][0]

    if ax is not None:
        for _p in ps:
            ax.plot(x[1:], np.log10(_p[1:]), color="silver", zorder=0)

        ax.plot(
            x[idx],
            np.log10(nfw.m_diff(np.power(10., x), c)[idx]),
            color="C0",
            linestyle="-",
            linewidth=4,
            zorder=2,
            label="stacked fit",
        )
        ax.plot(
            x[idx],
            np.log10(p[idx]),
            color="C1",
            marker="o",
            zorder=2,
            label="median profile",
        )
        ax.axvline(
            np.log10(1.0 / c), color="C0", linestyle="--", label="$R_{-2}$"
        )

        ax.set_xlim([-2.2, 0.2])
        ax.set_ylim([-3.5, -0.5])
        ax.set_xlabel(r"$\log_{10}(R / R_{200 crit})$")
        ax.set_ylabel(r"$\log_{10}(M(R) / M_{200 crit})$")
        ax.legend()

    return (
        c,
        idx,
        x,
        np.log10(np.median(np.cumsum(ps, axis=1), axis=0)),
        np.log10(nfw.m_diff(np.power(10.0, x), c)),
        np.log10(p),
    )


def cmh(haloes, grav, snap, f=0.02, F=0.1, ax=None):
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

    if ax is not None:
        for _m in ms:
            ax.plot(np.log10(rho), np.log10(_m), color="silver")

        ax.plot(
            np.log10(rho),
            np.log10(m),
            color="C1",
            marker="o",
            label="median mass history",
        )
        ax.axvline(
            rho_f, color="C0", linestyle="--", label="formation threshold"
        )

        ax.set_xlim([0.2, 2.2])
        ax.set_ylim([-2.0, 0.5])
        ax.set_xlabel(r"$\log_{10}(rho_crit(z) / rho_{crit}(z_0)$")
        ax.set_ylabel(r"$\log_{10}(M_{200 crit}(z) / M_{200 crit}(z_0)$")
        ax.legend()

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
        rho_s = np.log10(nfw.rho_enc(rs_f / c, c))
        F = nfw.m(rs_f / c, c)
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

    # bin = 10
    # snap = 122
    # grav = "GR_b64n512"
    # f = 0.02
    # rs_f = 1.0
    # reader = HBTReader("./data/%s/subcat" % grav)
    # haloes, _, _ = mf(reader, grav, snap, nbins)
    # print(process(haloes[haloes["bin"] == bin], grav, snap, f, rs_f, bin))

    rs_f, f = 1.0, 0.02
    sys.stdout.write("prof,rs_f,grav,snap,f,bin,counts,rho_f,rho_s\n")
    for grav in ["GR_b64n512", "fr6_b64n512"]:
        reader = HBTReader("./data/%s/subcat" % grav)
        for snap in [122, 93, 78, 61, 51]:
            # for rs_f in [0.3, 1.0, 2.0]:
            #     for f in [0.01, 0.02, 0.1]:
            haloes, _, counts = mf(reader, grav, snap, nbins)
            for i, count in enumerate(counts):
                rho_f, rho_s = process(
                    haloes[haloes["bin"] == i + 1], grav, snap, f, rs_f, i + 1
                )
                sys.stdout.write(
                    "%s,%.2f,%s,%d,%.2f,%d,%d,%f,%f\n"
                    % ("nfw", rs_f, grav, snap, f, i + 1, count, rho_f, rho_s)
                )
