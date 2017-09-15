#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

from src import read
from src import process

h = 0.697
Rho0 = 147.7543 #rho_crit(z = 0) in M_solar/kpc^3
OmegaM = 0.281
OmegaL = 1. - OmegaM

def rho_c(z = 0.0):
  return Rho0*(OmegaM*np.power(1.0 + z, 3.)+OmegaL)

def prof(ax, d):
	ax.set_title("FoF group density profile")
	ax.set_xlabel(r"$\log_{10}(R/R_{200})$")
	ax.set_ylabel(r"$\log_{10}(N(\mathrm{shell}) / N(< R_{200}))$")
	
	x = np.linspace(-2.5, 0.0, 32)
	d = np.array(d, dtype=np.float32)

	# # cumulative
	# d = process.normalise(d)

	# # remove funny bins
	# x = x[:-2]
	# d = d[:,:-2]

	# differential
	d = np.divide(d.T, np.cumsum(d, axis=1)[:,-1]).T

	for row in d:
		ax.plot(x, np.log10(row), color='grey')
	
	ax.plot(x, np.log10(process.stack(d)),\
		color='red', linewidth=2)

def cmh(ax, d, isnap=122):
	ax.set_title("FoF group collapsed mass history")
	ax.set_xlabel(r"$\log_{10}(\rho_c(z) / \rho_c(z_0))$")
	ax.set_ylabel(r"$\log_{10}(M_{200}\mathrm{progenitors})$")

	z = read.snaps()
	x = rho_c(np.array([z[z['Snapshot'] == s][0]['Redshift']\
		for s in map(lambda s: int(s), d.columns)]))
	x = x/rho_c(z[z['Snapshot'] == isnap][0]['Redshift'])

	d = process.normalise(d)
	
	for row in d:
		ax.plot(np.log10(x), np.log10(row), color='grey')
	ax.plot(np.log10(x), np.log10(process.stack(d)),\
		color='red', linewidth=2)

if __name__ == '__main__':
	snap = int(sys.argv[1])
	z = read.snaps()
	z0 = z[z['Snapshot'] == snap][0]['Redshift']

	fig, ax = plt.subplots(figsize=(13,6), nrows=1, ncols=2)
	fig.suptitle("Snapshot %d, $z_0=%.2f$"%(snap,z0))

	# bin haloes by mass
	idx = list(read.prop(snap)[:999]['M200Crit_bin'] == 9)

	d = read.prop(snap)[:999]
	print process.count_grouped(d['M200Crit_bin'])

	data_cmh = read.cmh(snap).head(999)[idx]
	cmh(ax[0], data_cmh, snap)

	data_prof = read.prof(snap).head(999)[idx]
	prof(ax[1], data_prof)

	fig.tight_layout()
	fig.subplots_adjust(top = 0.9)
	# plt.show()
	plt.savefig("%03d.pdf"%snap)
