#!/usr/bin/env python
import sys
import numpy as np

from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG
import read
import traverse

def get(h, d):
	"""Returns halo (row of data) given a ``nodeIndex``
	
	The implementation is idempotent, so that when it does receive an actual halo,
	it returns the unchanged data row.

	Arguments:
		h (int): ``nodeIndex`` queried
		d (numpy.ndarray): DHalo tree data, as provided by :mod:`src.read`
	Return:
		h (numpy.ndarray): row of argument ``d`` of the given ``nodeIndex``
	"""

	if (type(h) == int or type(h) == np.int64):
		h = 0 if h is -1 else h
		h = d[np.where(d[:,ID] == h)][0]
	elif type(h) == np.ndarray:
		pass
	else:
		raise TypeError("Halo must be either ID or a NumPy array, not %s"%(type(h)))
	return h

def progenitors(h, d):
	"""Finds progenitors of ``h``

	The following search is employed:

	- find all haloes of which ``h`` is a **host of a descendant**
	- find hosts of **these haloes**
	- keep unique ones
	"""
	h = get(h, d)
	return np.unique(d[np.where(d[:,DESC_HOST] == h[ID])][:,HOST])

def host(h, d):
	"""Finds host of ``h``

	Recursively continues until hits the main halo, useful for potentially
	multiply embedded subhaloes.
	"""
	# return d[np.where(d[:,ID] == h[HOST])][0]
	h = get(h, d)
	if h[HOST] == h[HOST]:
		return h
	else:
		host(d[np.where(d[:,ID] == h[HOST])][0], d)

def is_main(h, d):
	"""Checks if halo is a main halo using :func:`host`
	"""
	h = get(h, d)
	result = True if h[ID] == h[HOST] else False
	return result

def descendant(h, d):
	"""Finds descendant of ``h``
	"""
	h = get(h, d)
	return d[np.where(d[:,ID] == h[DESC])][0]

def descendant_host(h, d):
	"""Finds host of a descendant of ``h``

	DHalo uses this value to keep track of the most massive part of subhaloes in
	case of splitting, preventing "multiply-progenitored" haloes.
	"""
	h = get(h, d)
	return d[np.where(d[:,ID] == h[DESC_HOST])][0]

def subhaloes(h, d):
	"""Finds haloes for which ``h`` is a host
	"""
	h = get(h, d)
	return d[np.where(d[:,HOST] == h[ID])][:,ID]

def mass(h, d):
	"""Finds mass of central halo and all subhaloes
	"""
	return np.sum(np.array(map(lambda ih: get(ih, d), subhaloes(h, d)))[:,MASS])

if __name__ == '__main__':
	d = read.retrieve()
	for id in map(int, sys.argv[1].split(",")):
		traverse.yaml_from_data(id, d, recursive=False)

