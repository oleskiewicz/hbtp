#!/usr/bin/env python
import sys, numpy as np
import read
from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG

def halo(h, d):
	"""
	Find halo given an ID.  Built-in fallback, so that when given halo it returns it.
	"""
	if type(h) == int:
		h = 0 if h is -1 else h
		h = d[np.where(d[:,ID] == h)][0]
	elif type(h) == np.ndarray:
		pass
	else:
		raise TypeError("Halo must be either ID or a NumPy array")
	return h

def display(h, d, level=0, list=False):
	"""
	Recursively print DHalo merger tree to a YAML file
	"""
	indent = "  "
	if h != -1:
		h = halo(h, d)

		if list:
			sys.stdout.write("%s- "%(indent*(level-1)))
		else:
			sys.stdout.write("%s"%(indent*level))
		print "id:   %d"%(h[ID])

		if (len(prog_host_ids) > 0):
			print "%sprog:"%(indent*(level))
			for prog_host_id in prog_host_ids:
				display(prog_host_id, level+1, True)
		else:
			print "%sprog: none"%(indent*(level))

		if (h[ID] == h[HOST]):
			print "%shost: self"%(indent*(level))
		else:
			print "%shost:"%(indent*(level))
			display(h[HOST], level+1)

		# if (h[DESC] == -1):
		# 	print "%sdesc: none"%(indent*(level))
		# else:
		# 	print "%sdesc:"%(indent*(level))
		# 	display(h[DESC], level+1)

	else:
		print "%sid: none"%(indent*level)

def hosts_of_progenitors(h, d):
	"""
	- find all haloes of which ``h`` is a descendant
	- find host of these haloes
	- keep unique ones
	"""
	h = halo(h, d)
	return np.unique(d[np.where(d[:,DESC] == h[ID])][:,HOST])

def host(h, d):
	"""
	- find host of ``h``
	"""
	h = halo(h, d)
	return d[np.where(d[:,ID] == h[HOST])][0]

def descendant(h, d):
	"""
	- find descendant of ``h``
	"""
	h = halo(h, d)
	return d[np.where(d[:,ID] == h[DESC])][0]

def subhaloes(h, d):
	"""
	- find haloes for which ``h`` is a host
	"""
	h = halo(h, d)
	return d[np.where(d[:,HOST] == h[ID])]

def progenitors(h, d, main=False):
	"""
	- find all haloes for which ``h`` is a descendant

	.. note:: this will include subhaloes
	"""
	h = halo(h, d)
	result = d[np.where(d[:,DESC] == h[ID])]
	if main:
		result = result[np.where(result[:,MAIN_PROG] == 1)][0]
	return result

def main():
	d = read.retrieve()
	for id in [48048400000000, 47048400000000,]:
		print host(id, d)
		print progenitors(id, d)
		print progenitors(id, d, True)
		print ""

if __name__ == '__main__':
	main()

