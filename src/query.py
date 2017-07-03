#!/usr/bin/env python
import sys, numpy as np
import read
from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG

def halo(h, d):
	"""
	Find halo given an ID.  Built-in fallback, so that when given halo it returns it.
	"""
	if (type(h) == int or type(h) == np.int64):
		h = 0 if h is -1 else h
		h = d[np.where(d[:,ID] == h)][0]
	elif type(h) == np.ndarray:
		pass
	else:
		raise TypeError("Halo must be either ID or a NumPy array, not %s"%(type(h)))
	return h

def display(h, d, level=1, list=True, recursive=False):
	h = halo(h, d)
	tab = "  "
	ind =tab*level

	if list:
		sys.stdout.write("%s- "%(tab*(level-1)))
	else:
		sys.stdout.write("%s"%(ind))
	print "id:\t%d"%(h[ID])

	print "%shost_id:\t%s"%(ind, "self" if h[ID] == h[HOST] else str(h[HOST]))

	hh = hosts_of_progenitors(h[ID], d)
	if (len(hh) > 0):
		if recursive:
			print "%sprog:"%(ind)
			for _h in hh:
				display(_h, d, level+1, True, True)
		else:
			print "%sprog:\t[%s]"%(ind, ",".join(map(str, hh)))
	else:
		print "%sprog: none"%(ind)

	hh = hosts_of_subprogenitors(h[ID], d)
	if (len(hh) > 0):
		if recursive:
			print "%shost_prog:"%(ind)
			for _h in hh:
				display(_h, d, level+1, True, True)
		else:
			print "%shost_prog:\t[%s]"%(ind, ",".join(map(str, hh)))
	else:
		print "%shost_prog: none"%(ind)

	# hh = subhaloes(h[ID], d)
	# if (len(hh) > 0):
	# 	if recursive:
	# 		print "%ssub:"%(ind)
	# 		for _h in hh:
	# 			display(_h, d, level+1, True, True)
	# 	else:
	# 		print "%ssub:\t[%s]"%(ind, ",".join(map(str, hh)))
	# else:
	# 	print "%ssubs: none"%(ind)

	# print "%sdesc_id:\t%s"%(ind, "none" if h[DESC] == -1 else str(h[DESC]))
	if (h[DESC] == -1):
		print "%sdesc_id:\tnone"%(ind)
	else:
		if recursive:
			print "%sdesc_id:"%(ind)
			display(h[DESC], d, level+1)
		else:
			print "%sdesc_id:\t%d"%(ind, h[DESC])

	# print "%sdesc_id:\t%s"%(ind, "none" if h[DESC] == -1 else str(h[DESC]))
	if (h[DESC_HOST] == -1):
		print "%sdesc_host:\tnone"%(ind)
	else:
		if recursive:
			print "%sdesc_host:"%(ind)
			display(h[DESC_HOST], d, level+1)
		else:
			print "%sdesc_host:\t%d"%(ind, h[DESC_HOST])

def hosts_of_progenitors(h, d):
	"""
	- find all haloes of which ``h`` is a descendant
	- find host of these haloes
	- keep unique ones
	"""
	h = halo(h, d)
	return np.unique(d[np.where(d[:,DESC] == h[ID])][:,HOST])

def hosts_of_subprogenitors(h, d):
	"""
	- find all haloes of which ``h`` is a host of a  descendant
	- find host of these haloes
	- keep unique ones
	"""
	h = halo(h, d)
	return np.unique(d[np.where(d[:,DESC_HOST] == h[ID])][:,HOST])

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

def descendant_host(h, d):
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
	return d[np.where(d[:,HOST] == h[ID])][:,ID]

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

def progenitor_hosts(h, d):
	"""
	- find all haloes which host ``h`` progenitors
	"""
	h = halo(h, d)
	result = np.unique(d[np.where(d[:,DESC_HOST] == h[ID])][:,HOST])
	return result

def main():
	d = read.retrieve()
	for id in map(int, sys.argv[1].split(",")):
		display(id, d)

if __name__ == '__main__':
	main()

