#!/usr/bin/env python
import sys
import numpy as np

from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG
import read

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

def display(h, d, level=1, recursive=False):
	"""Print halo in a YAML format

	Can be run recursively (to generate a tree-like representation for all
	progenitors, provided by :func:`progenitors`), or non-recursively, and
	then it only prints one halo and ``nodeIndex`` values of all progenitors.

	Arguments:
		h (int): ``nodeIndex`` queried
		d (numpy.ndarray): DHalo tree data, as provided by :func:`src.read.data`
		level (int): (default=1) used to increase level counter if printed
			recursively
		recursive (bool): (default=False) if ``True``, descends every time a foreign
			key is encountered;  if ``False``, only prints the IDs
	"""

	if not is_main(h, d): raise ValueError("Not a host halo!")

	h = get(h, d)
	tab = "  "
	ind = tab*level

	# HALO
	sys.stdout.write("%s- "%(tab*(level-1)))
	print "halo: %d"%(h[ID])
	print "%ssnap: %d"%(ind, h[SNAP])
	print "%smass: %d"%(ind, halo.mass(h, d))
	print "%shost: %s"%(ind, "self" if h[HOST] == h[ID] else str(h[HOST]))

	# SUBHALOES
	print "%ssub: [%s]"%(ind, ",".join(map(str, subhaloes(h, d))))

	# DESCENDANTS
	print "%sdesc: %d"%(ind, h[DESC])
	print "%sdesc_host: %d"%(ind, h[DESC_HOST])

	# PROGENITORS
	hh = progenitors(h, d)
	if (len(hh) > 0):
		if recursive:
			print "%sprog:"%(ind)
			for _h in hh:
				yaml_from_data(_h, d, level+1, True)
		else:
			print "%sprog: [%s]"%(ind, ",".join(map(str, hh)))
	else:
		print "%sprog: -1"%(ind)

if __name__ == '__main__':
	d = read.retrieve()
	for id in map(int, sys.argv[1].split(",")):
		display(id, d, recursive=False)

