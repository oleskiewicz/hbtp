#!/usr/bin/env python
import sys
import logging
from logging.config import fileConfig
import numpy as np

from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG, columns
import halo

def node(h, m, m0, nfw_f):
	return "\t%d [label=\"%s (%d, %d, %d)\", style=filled, fillcolor=%s];\n"%(\
		h[ID], "%d"%(h[ID]) if h[DESC] == h[DESC_HOST] else "%d > %d"%(h[ID], h[DESC]), \
		h[MAIN_PROG], m, h[SNAP], "green" if m > nfw_f*m0  else "red")

def tree(file, t, d, m0, nfw_f):
	"""Generates Dot graph from merger tree

	Every node is formatted as follows::

		[nodeIndex | nodeIndex > descendantIndex (if not merging into main)] (isMainProgenitor, particleNumber, snapshotNumber)

	and is colour coded:

	- green: halo mass exceeds fraction :math:`f`
	- red: halo mmass too small, does not count towards the assembly history

	Arguments:
		file (File): file with Dot output
		t (list): merger tree generated by :func:`tree_from_data`
		d (numpy.ndarray): dataset provided by :mod:`src.read` module
		m0 (int): mass of the final halo
		nfw_f (float): (default=0.01) NFW :math:`f` parameter
	"""
	file.write(node(halo.get(t[0], d), halo.mass(t[0], d), m0, nfw_f))
	for i,_ in enumerate(t[1]):
		file.write( "\t%d -> %d;\n"%(t[1][i][0], t[0]))
		tree(file, t[1][i], d, m0, nfw_f)

def mah(file, m, progs):
	"""Generates a Dot subgraph with snaphot numbers and progenitors' masses

	Arguments:
		file (File): file with Dot output
		m (numpy.ndarray): mass assembly history generated by
			:func:`src.tree.mah`, in a ``[ nodeIndex, snapshotNumber,
			sum(particleNumber) ]`` format
		progs (numpy.ndarray): slice of ``data`` containing only progenitors
	"""
	file.write("\t%s;"%(" -> ".join(["snap_%02d\n"%(s[1]) for s in m])))
	for s in m:
		file.write("\tsnap_%02d [label=\"(%d, %02d)\"];\n"%(s[1], s[2], s[1]))
		file.write("\t{ rank=same; snap_%02d; %s };"%(s[1], "; \n".join(\
			map(str, progs[np.where(progs[:,SNAP] == s[1])][:,ID]))))

