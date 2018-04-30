#!/usr/bin/env python
import sys
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.hbtp.HBTReader import HBTReader
from src import read
from src import cosmology
from src import einasto
from src import nfw


def mf(ax, bins, counts, bin=0, **kwargs):
    """Plots FoF halo mass function
	"""
    ax.plot(bins, np.log10(counts), **kwargs)
    # if bin != 0:
    # 	ax.axvspan(bin_edges[bin-1], bin_edges[bin], alpha=0.5)


def smf(ax, bins, counts, **kwargs):
    """Plots subhaloes
	"""
    ax.plot(bins, np.log10(counts), **kwargs)


def prof(ax, idx, x, y_med, y_fit, ys=None):
    """Plots binned particle profiles for FoF haloes
	"""
    ax.set_xlabel(r'$\log_{10}(r/r_{200})$')
    ax.set_ylabel(r'$\log(M(r)/M(r<r_{200}))$')

    ax.plot(x[idx], y_fit[idx],\
     color='C0', linewidth=4, zorder=1)
    ax.plot(x[idx], y_med[idx],\
     color='C1', marker='o', zorder=2,\
     label='median density profile')

    if ys is not None:
        [ax.plot(x, _, color='grey', zorder=0) for _ in ys]

    ax.legend(loc='lower right')


def cmh(ax, x, y_med, x_fit, y_fit, ys=None):
    """Plots CMHs of FoF haloes
	"""
    ax.set_xlabel(r'$\log_{10}(\rho_{crit}(z)/\rho_{crit}(z_0))$')
    ax.set_ylabel(r'$\log_{10}(\Sigma_i(M_{i,200})/M_{200}(z=z_0))$')

    ax.plot(x, y_med,\
     color='C1', marker='o',\
     label='median CMH')

    ax.axhline(y_fit,\
     color='C0', linestyle='-.')
    ax.axvline(x_fit,\
     color='C0', linestyle='--',\
     label=r'formation time $\rho_{crit} = %.2f$'%x_fit)

    if ys is not None:
        [ax.plot(x, _, color='grey', zorder=0) for _ in ys]

    ax.legend(loc='lower left')


def process(snap, hs, bin):
    zs = read.snaps()
    z0 = zs[zs['Snapshot'] == snap][0]['Redshift']

    hs = hs[hs['bin'] == bin]

    logging.info('Snapshot %d, bin %d, %d haloes' % (snap, bin, len(hs)))

    c = -1.0
    rho_f = -1.0
    try:
        c = prof(hs)
        rho_s = np.log10(nfw.rho_enc(1.0 / c, c))
        F = nfw.m_enc(1.0 / c, c)
        try:
            rho_f = cmh(hs, snap, F)
        except:
            logging.error('Unable to calculate formation time')
    except:
        logging.error('Unable to fit density profile')

    return c


def concentration_mass(ax, m, c):
    """Plots concentration mass relation at a given snapshot
	"""
    ax.set_xlabel(r'$\log_{10}M_{200}$')
    ax.set_ylabel(r'$\log_{10}c$')
    ax.set_ylim([0.4, 1.4])
    ax.plot(m, c, '.')
    ax.plot(np.array([11.0, 14.0]), np.array([0.93, 0.65]), '-')


if __name__ == '__main__':
    snap = int(sys.argv[1])
    r = HBTReader('./data')
    nbins = 100
    bin = 10

    fig, ax = plt.subplots(1)
    hs, _, m = mf(ax, snap, nbins)
    _ = cmh(snap, hs[hs['bin'] == bin], ax=ax)
    # _ = concentration_mass(r, snap, nbins, ax)
    plt.show()

    # with open('./output/einasto.csv', 'w') as f:
    # 	f.write('snap,bin,rho_f,rho_s\n')
    # 	for snap in [51,61,78,93,122]:
    # 		hs, _, bins = mf(r, snap, nbins)
    # 		for bin in range(1, nbins+1):
    # 			try:
    # 				rho_f, rho_s = process(r, snap, hs, bin)
    # 				f.write('%d,%d,%f,%f\n'%(snap, bin, rho_f, rho_s))
    # 			except:
    # 				logging.info('Failed snapshot %d, bin %d'%(snap, bin))

    # ds = np.genfromtxt('./output/einasto.csv',\
    #		delimiter=',', skip_header=1,\
    #		dtype=np.dtype([\
    #			('snap',int),\
    #			('bin',int),\
    #			('rho_f',float),\
    #			('rho_s',float)\
    # ]))

    # markers = [['o', None], ['.', None], ['^', None], ['x', None], ['*', None]]
    # for i,snap in enumerate(snaps):
    #		for d in ds[ds['snap'] == snap]:
    #			plt.scatter(d['rho_f'], d['rho_s'],\
    #				color='C%d'%d['bin'], marker=markers[i][0])
    #			markers[i][1] = plt.Line2D([], [], label='snap %d'%snap,\
    #				color='k', marker=markers[i][0], linestyle='')

    # plt.xlabel(r'$\log_{10}(\rho_{crit}(z_{form})/\rho_{crit}(z_0))$')
    # plt.ylabel(r'$\log_{10}(\langle\rho_{s}\rangle/\rho_{crit}(z_0))$')
    # plt.xlim((0.2, 1.6))
    # plt.ylim((2.8,4.2))

    # plt.legend(handles=[markers[i][1] for i in range(len(snaps))], loc='lower right')
    # plt.savefig('./einasto.pdf')
