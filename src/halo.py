#!/usr/bin/env python
import sys
import numpy as np

from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG
import read
import traverse

def get(h, d):
	"""Finds halo given a ``nodeIndex``
	
	Built-in fallback, so that when given halo it returns it.

	Arguments:
		h (int): ``nodeIndex`` queried
		d (numpy.ndarray): DHalo tree data, as provided by :mod:`src.read`
	"""

	if (type(h) == int or type(h) == np.int64):
		h = 0 if h is -1 else h
		h = d[np.where(d[:,ID] == h)][0]
	elif type(h) == np.ndarray:
		pass
	else:
		raise TypeError("Halo must be either ID or a NumPy array, not %s"%(type(h)))
	return h

def all_progenitors(tree, key):
	"""Finds all halo IDs belonging to a given merger tree

	**Acknowledgements:**
		https://stackoverflow.com/a/9807955
	"""
	if key in tree:
		yield tree[key]
	for node in tree:
		if isinstance(tree[node], list):
			for i in tree[node]:
				for j in all_progenitors(i, key):
					yield j

def progenitors(h, d):
	"""
	Finds progenitors of halo ``h``:

	- find all haloes of which ``h`` is a **host of a descendant**
	- find host of **these haloes**
	- keep unique ones
	"""
	h = get(h, d)
	return np.unique(d[np.where(d[:,DESC_HOST] == h[ID])][:,HOST])

def host(h, d):
	"""Finds host of ``h``
	"""
	h = get(h, d)
	if h[HOST] == h[HOST]:
		return h
	else:
		host(d[np.where(d[:,ID] == h[HOST])][0], d)
	# return d[np.where(d[:,ID] == h[HOST])][0]

def is_main(h, d):
	"""Checks if halo is a subhalo, or a main FoF group
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
	"""Finds host--descendant of ``h``
	"""
	h = get(h, d)
	return d[np.where(d[:,ID] == h[DESC_HOST])][0]

def subhaloes(h, d):
	"""Finds haloes for which ``h`` is a host
	"""
	h = get(h, d)
	return d[np.where(d[:,HOST] == h[ID])][:,ID]

if __name__ == '__main__':
	d = read.retrieve()
	for id in map(int, sys.argv[1].split(",")):
		traverse.write_yaml(id, d, get(id, d)[MASS], recursive=True)

