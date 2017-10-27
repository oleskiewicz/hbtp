#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

if __name__ == '__main__':
	ds = {g: np.genfromtxt('/gpfs/data/dc-oles1/merger_trees/output/%s/nfw.csv'%g,\
		delimiter=',', skip_header=1, dtype=np.dtype([\
		('snap',int),\
		('bin',int),\
		('rho_f',float),\
		('rho_s',float),\
	])) for g in ['gr', 'fr']}

	markers = [['o', None], ['s', None], ['^', None], ['*', None], ['x', None]]
	colours = [['C0', None], ['C1', None]]

	for i,snap in enumerate(np.unique(ds['gr']['snap'])):
		for j,g in enumerate(ds):
			for d in ds[g][ds[g]['snap'] == snap]:
				plt.scatter(d['rho_f'], d['rho_s'],\
					color=colours[j][0], marker=markers[i][0])
				markers[i][1] = plt.Line2D([], [], label='snap %d'%snap,\
					color='k', marker=markers[i][0], linestyle='')
				colours[j][1] = plt.Line2D([], [], label=g,\
					color=colours[j][0], marker='o', linestyle='')

	# plt.plot(np.linspace(0.2, 1.6), 2.65+np.linspace(0.2, 1.6), 'k--')

	plt.xlabel(r'$\log_{10}(\rho_{crit}(z_{form})/\rho_{crit}(z_0))$')
	plt.ylabel(r'$\log_{10}(\langle\rho_{s}\rangle/\rho_{crit}(z_0))$')
	plt.xlim((0.2, 1.6))
	plt.ylim((2.8, 4.2))

	l1 = plt.legend(handles=[markers[i][1] for i in range(len(markers))], loc='lower right')
	l2 = plt.legend(handles=[colours[j][1] for j in range(len(colours))], loc='upper left')
	plt.gca().add_artist(l1)

	plt.savefig('./compare_nfw.pdf')
