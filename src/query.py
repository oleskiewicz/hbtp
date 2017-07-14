#!/usr/bin/env python
import sys
import numpy as np

import read
from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG, columns

def process(data, query):
	"""Process query on a data set

	Example:

		This query retuns halo IDs for top 100 most massive haloes at snapshot 30:

		.. code-block:: python

			q = {
				'filter': {
					'by': SNAP,
					'value': 30,
				},
				'sort': {
					'by': MASS,
				},
				'limit': {
					'n': 100,
				},
				'select': {
					'by': ID,
				},
			}

	Arguments:
		data (numpy.ndarray): dataset provided by :mod:`src.read` module
		query (dict): query to be processed (see `Example`)
	"""
	data = data[np.where(data[:,query['filter']['by']] == query['filter']['value'])]
	return data[data[:,query['sort']['by']].argsort()[::-1]][0:query['limit']['n'],ID]

if __name__ == '__main__':
	d = read.retrieve()

	q = {
		'filter': {
			'by': SNAP,
			'value': 30,
		},
		'sort': {
			'by': MASS,
		},
		'limit': {
			'n': 100,
		},
		'select': {
			'by': ID,
		},
	}

	ids = process(d, q)

	with open(sys.argv[1], 'w') as f:
		for i in ids:
			f.write("%d\n"%i)
