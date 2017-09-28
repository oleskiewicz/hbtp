#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from src.hbtp.HBTReader import HBTReader
from src import read
from src import cosmology
from src import nfw

def subhalo_mf(snap, reader, ax=None):
	"""Selects, bins & bins subhaloes into 20 log-spaced bins
	"""
	ss = reader.LoadSubhalos(snap)
	ss = ss[(ss['HostHaloId'] != -1) & (ss['BoundM200Crit'] > 0.0)& (ss['Nbound'] >= 20)]

	counts, bin_edges = np.histogram(np.log10(ss['BoundM200Crit']), 20)
	ss = np.lib.recfunctions.append_fields(ss, 'bin',\
		np.digitize(np.log10(ss['BoundM200Crit']), bin_edges),\
		usemask=False)
	bins = 0.5*(bin_edges[1:] + bin_edges[:-1])

	if ax is not None:
		ax.plot(bins, np.log10(counts), marker='.')
	
	return ss, counts

def halo_mf(snap, reader, ax=None):
	"""Selects, bins & bins FoF haloes into 10 log-spaced bins
	"""
	hs = reader.LoadHostHalos(snap)[['HaloId','R200CritComoving','M200Crit']]
	hs = hs[hs['M200Crit'] >= 20]
	hs['M200Crit'] = 1e10*hs['M200Crit']

	counts, bin_edges = np.histogram(np.log10(hs['M200Crit']), 10)
	hs = np.lib.recfunctions.append_fields(hs, 'bin',\
		np.digitize(np.log10(hs['M200Crit']), bin_edges),\
		usemask=False)
	bins = 0.5*(bin_edges[1:] + bin_edges[:-1])

	if ax is not None:
		ax.plot(bins, np.log10(counts), marker='.')
		ax.axvspan(bin_edges[bin-1], bin_edges[bin], color='grey', alpha=0.5)

	return hs, counts, bin_edges

def prof(snap, reader, haloes, ax=None):
	"""Reads, fits & plots binned particle profiles for FoF haloes
	"""
	ps = np.array(\
		reader.LoadHostHalos(snap, [list(haloes['HaloId']),])['Profile'],\
		dtype=np.float)
	ps = np.divide(ps.T, np.sum(ps, axis=1)).T
	p = np.mean(ps, axis=0)

	x = np.linspace(-2.0, 0.0, 20)

	c,c_err = nfw.fit(np.power(10.0,x), p)

	if ax is not None:
		ax.set_xlabel(r'$\log_{10}(r/r_{200})$')
		ax.set_ylabel(r'$\log(M(r)/M(r<r_{200}))$')
		ax.plot(x, np.log10(nfw.m_diff(np.power(10.,x), c)),\
			color='C0', linewidth=4, zorder=1,\
			label='NFW fit ($c=%.2f^{+%.2f}_{-%.2f}$)'%(c,c_err[1]-c,c-c_err[0]))
		ax.fill_between(x,\
			np.log10(nfw.m_diff(np.power(10.,x), c_err[0])),\
			np.log10(nfw.m_diff(np.power(10.,x), c_err[1])),
			color='C0', alpha=0.2, zorder=1,\
			label=r'NFW fit FWHM')
		[ax.plot(x, np.log10(_), color='grey', zorder=0) for _ in ps]
		ax.plot(x, np.log10(p), \
			color='C1', marker='o', zorder=2,\
			label='average density profile')
		ax.legend(loc='lower right')

	return c, c_err

def cmh(snap, reader, haloes, F=0.1, ax=None):
	"""Reads, calculates formation time of & plots CMHs of FoF haloes
	"""
	ms = np.array(read.cmh(snap).loc[haloes['HaloId']], dtype=np.float)
	ms = np.divide(ms.T, ms[:,-1]).T
	m = np.mean(ms, axis=0)

	zs = read.snaps()
	z0 = zs[zs['Snapshot'] == snap][0]['Redshift']
	rho = cosmology.rho_c(\
		np.array([zs[zs['Snapshot'] == s][0]['Redshift']\
		for s in np.arange(1+snap-ms.shape[1], 1+snap)]))\
		/ cosmology.rho_c(z0)

	rho_form = rho[np.where(m > F*m[-1])][0]
	rho_form_err = [rho[np.where(m > F*m[-1])][1], rho[np.where(m < F*m[-1])][-1]]

	if ax is not None:
		ax.set_xlabel(r'$\log_{10}(\rho_{crit}(z)/\rho_{crit}(z_0))$')
		ax.set_ylabel(r'\log_{10}($\Sigma_i(M_{i,200})/M_{200}(z=z_0))$')
		[ax.plot(np.log10(rho), np.log10(_), color='grey') for _ in ms]
		ax.plot(np.log10(rho), np.log10(m),\
			color='C1', marker='o',\
			label='average CMH')
		ax.axhline(np.log10(F*m[-1]),\
			color='C0', linestyle='-.',
			label=r'formation time $\rho_{crit} = %.2f$'%rho_form)
		ax.axvline(np.log10(rho_form),\
			color='C0', linestyle='--',\
			label='formation threshold $F = %.2f$'%F)
		ax.axvspan(np.log10(rho_form_err[0]), np.log10(rho_form_err[1]),\
			color='C0', linestyle='--', alpha=0.5, zorder=1)
		ax.legend(loc='lower left')

	return rho_form, rho_form_err, z0

if __name__ == '__main__':
	snap = int(sys.argv[1])
	bin = int(sys.argv[2])

	r = HBTReader('./data/')

	fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(12.8, 8.3))
	hs, mf, bins = halo_mf(snap, r)
	hs = hs[hs['bin'] == bin]
	c, c_err = prof(snap, r, hs, ax[0])
	rho_form, rho_form_err, z0 = cmh(snap, r, hs, 0.1, ax[1])

	plt.tight_layout()
	fig.suptitle(r'$z=%.2f$, %d haloes, $%.2f < \log_{10}(M_{200}/M_{\odot}) < %.2f$'\
		%(z0, len(hs), bins[bin-1], bins[bin]))
	plt.savefig('./plot.pdf')
