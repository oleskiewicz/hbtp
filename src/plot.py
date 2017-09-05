#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt

from src import read
from src import process

h = 0.697
Rho0 = 147.7543 #rho_crit(z = 0) in M_solar/kpc^3
OmegaM = 0.281
OmegaL = 1. - OmegaM

def rho_c(z = 0.0):
  return Rho0*(OmegaM*np.power(1.0 + z, 3.)+OmegaL)

def prof(ax, d):
	x = np.logspace(-2.5, 0.0, 32)
	d = process.normalise(d)
	
	for row in d:
		ax.plot(x, np.log10(row), color='grey')
	
	ax.plot(x, np.log10(process.stack(d)),\
		color='red', linewidth=2)

def cmh(ax, d):
	z =  read.snaps()
	x = rho_c(np.array([z[z['Snapshot'] == s][0]['Redshift']\
		for s in map(lambda s: int(s), d.columns)]))

	d = process.normalise(d)
	
	for row in d:
		ax.plot(np.log10(x), np.log10(row), color='grey')
	ax.plot(np.log10(x), np.log10(process.stack(d)),\
		color='red', linewidth=2)

if __name__ == '__main__':
	snap = int(sys.argv[1])
	fig, ax = plt.subplots(1)
	d = read.cmh(snap).head(20)
	cmh(ax, d)
	plt.savefig("test.pdf")
