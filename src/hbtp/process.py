#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

from src.hbtp.HBTReader import HBTReader
from src import read
from src import cosmology
from src import einasto

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

def halo_mf(snap, reader, nbins, ax=None):
	"""Selects, bins & bins FoF haloes into 10 log-spaced bins
	"""
	hs = reader.LoadHostHalos(snap)\
		[['HaloId', 'R200CritComoving', 'M200Crit', 'CenterOffset']]
	hs = hs[(hs['M200Crit'] >= 20) & (hs['CenterOffset'] >= 0.1)]
	hs['M200Crit'] = 1e10*hs['M200Crit']

	counts, bin_edges = np.histogram(np.log10(hs['M200Crit']), nbins)
	hs = np.lib.recfunctions.append_fields(hs, 'bin',\
		np.digitize(np.log10(hs['M200Crit']), bin_edges),\
		usemask=False)
	bins = 0.5*(bin_edges[1:] + bin_edges[:-1])

	if ax is not None:
		ax.plot(bins, np.log10(counts), marker='.')
		ax.axvspan(bin_edges[bin-1], bin_edges[bin], color='grey', alpha=0.5)

	return hs, counts, bins

def prof(reader, snap, haloes, ax=None):
	"""Reads, fits & plots binned particle profiles for FoF haloes
	"""
	ps = np.array(\
		reader.LoadHostHalos(snap, [list(haloes['HaloId']),])['Profile'],\
		dtype=np.float)
	xmin = 0.5 * np.cbrt((4.0*np.pi)/(3.0*np.sum(np.median(ps, axis=0))))
	xmax = 0.8
	x = np.linspace(-2.0, 0.0, 20)
	idx = np.where((np.power(10,x) < xmax) & (np.power(10,x) > xmin))

	ps = np.divide(ps.T, np.sum(ps, axis=1)).T
	p = np.median(ps, axis=0)

	c, a, chi2 = einasto.fit(\
		p,
		lambda c, a: einasto.m(np.power(10,x), c, a),\
		np.linspace(1.0, 10.0, 100),\
		np.linspace(0.01, 0.99, 100))

	if ax is not None:
		ax.set_xlabel(r'$\log_{10}(r/r_{200})$')
		ax.set_ylabel(r'$\log(M(r)/M(r<r_{200}))$')
		ax.plot(x[idx], np.log10(einasto.m(np.power(10,x), c, a)[idx]),\
			color='C0', linewidth=4, zorder=1,\
			label=r'fit ($c=%.2f$)'%(c))
		# ax.fill_between(x,\
		#		np.log10(nfw.m_diff(np.power(10.,x), c_err[0])),\
		#		np.log10(nfw.m_diff(np.power(10.,x), c_err[1])),
		#		color='C0', alpha=0.2, zorder=1,\
		#		label=r'NFW fit FWHM')
		[ax.plot(x, np.log10(_), color='grey', zorder=0) for _ in ps]
		ax.plot(x[idx], np.log10(p[idx]),\
			color='C1', marker='o', zorder=2,\
			label='average density profile')
		ax.axvline(np.log10(1.0/c), color='C0',\
			linestyle='--',\
			label=r'$r_s$')
		ax.legend(loc='lower right')

	return c, a

def cmh(reader, snap, haloes, F=0.1, ax=None):
	"""Reads, calculates formation time of & plots CMHs of FoF haloes
	"""
	ms = np.array(read.cmh(snap).loc[haloes['HaloId']], dtype=np.float)
	ms = np.divide(ms.T, ms[:,-1]).T
	m = np.median(ms, axis=0)

	zs = read.snaps()
	z0 = zs[zs['Snapshot'] == snap][0]['Redshift']
	rho = cosmology.rho_c(\
		np.array([zs[zs['Snapshot'] == s][0]['Redshift']\
		for s in np.arange(1+snap-ms.shape[1], 1+snap)]))\
		/ cosmology.rho_c(z0)

	m_f = F*m[-1]
	y1, y2 = m[m > m_f][0], m[m < m_f][-1]
	x1, x2 = rho[m > m_f][0], rho[m < m_f][-1]
	rho_f = (np.log10(x1/x2)/np.log10(y1/y2))*(np.log10(m_f/y1))+np.log10(x1)

	if ax is not None:
		ax.set_xlabel(r'$\log_{10}(\rho_{crit}(z)/\rho_{crit}(z_0))$')
		ax.set_ylabel(r'$\log_{10}(\Sigma_i(M_{i,200})/M_{200}(z=z_0))$')
		[ax.plot(np.log10(rho), np.log10(_), color='grey') for _ in ms]
		ax.plot(np.log10(rho), np.log10(m),\
			color='C1', marker='o',\
			label='average CMH')
		ax.axhline(np.log10(m_f),\
			color='C0', linestyle='-.',
			label=r'formation threshold $F = %.2f$'%F)
		ax.axvline(rho_f,\
			color='C0', linestyle='--',\
			label=r'formation time $\rho_{crit} = %.2f$'%rho_f)
		ax.legend(loc='lower left')

	return rho_f

def process(reader, snap, hs, bin):
	zs = read.snaps()
	z0 = zs[zs['Snapshot'] == snap][0]['Redshift']

	# hs, mf, bins = halo_mf(snap, reader)
	hs = hs[hs['bin'] == bin]

	log.info('Snapshot %d, bin %d, %d haloes'%(snap, bin, len(hs)))

	try:
		c, a = prof(reader, snap, hs)
		rho_s = np.log10(einasto.rho_enc(1.0/c, c, a))
		F = einasto.m_enc(1.0/c, c, a)
		try:
			rho_f = cmh(reader, snap, hs, F)
		except:
			log.error('Unable to calculate formation time')
			rho_f = -1.0
	except:
		log.error('Unable to fit density profile')
		c = -1.0

	# return rho_f, rho_s
	return c, rho_f

def concentration_mass(reader, snap, ax=None):
	"""Plots concentration mass relation at a given snapshot
	"""

	hs, _, m = halo_mf(snap, reader, 10)
	c = np.array([np.log10(prof(reader, snap, hs[hs['bin'] == bin]))\
		for bin in range(1,11)]).T

	# if ax is not None:
	# 	ax.set_xlabel(r'$\log_{10}M_{200}$')
	# 	ax.set_ylabel(r'$\log_{10}c_{200}$')
	# 	ax.plot(m, c[0], '.')

	return c[0], c[1], m

def formation_mass(reader, snap, ax=None):
	"""Plots concentration mass relation at a given snapshot
	"""

	hs, _, m = halo_mf(snap, reader, 10)
	c = concentration_mass(reader, snap)
	
	rho_f = cmh(reader, snap, hs, einasto.m_enc(np.divide(1.0, c[0]), c[0], c[1]))

	# if ax is not None:
	# 	ax.set_xlabel(r'$\log_{10}M_{200}$')
	# 	ax.set_ylabel(r'$\log_{10}rho_{f}$')
	# 	ax.plot(m, rho_f, '.')

	return rho_f, m

if __name__ == '__main__':
	nbins = 5
	snap = int(sys.argv[1])
	r = HBTReader('./data')

	hs, _, m = halo_mf(snap, r, nbins)
	print [process(r, snap, hs, bin) for bin in range(1, nbins+1)]

	# with open('./output/einasto.csv', 'w') as f:
	# 	f.write('snap,bin,rho_f,rho_s\n')
	# 	for snap in [51,61,78,93,122]:
	# 		hs, _, bins = halo_mf(snap, r, nbins)
	# 		for bin in range(1, nbins+1):
	# 			try:
	# 				rho_f, rho_s = process(r, snap, hs, bin)
	# 				f.write('%d,%d,%f,%f\n'%(snap, bin, rho_f, rho_s))
	# 			except:
	# 				log.info('Failed snapshot %d, bin %d'%(snap, bin))

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
