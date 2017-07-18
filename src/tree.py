#!/usr/bin/env python
import sys
import logging
from logging.config import fileConfig
import numpy as np

from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG, columns
import read
import halo
import dot

def build(log, id, data):
	"""Generates merger tree from data

	Recursively calls itself inside the return statement, generating a merger tree
	of the format::
	
		[1, [[2, []], [3, [[4, []], [5, []]]], [6, []]]]

	equivalent to::

		1
			2
			3
				4
				5
			6

	Arguments:
		log (logging.Logger): log handling object
		id (int): ``nodeIndex`` of the starting halo
		data (numpy.ndarray): dataset provided by :mod:`src.read` module
	Returns:
		list: merger tree in a deeply mebedded format, rooted at the starting halo
	"""
	if not halo.is_main(id, d): raise ValueError("Not a host halo!")

	h = halo.get(id, data)
	progenitors = halo.progenitors(h, data)
	#TODO: [1, [[2, []], [3, [[4, []], [5, []]]], [6, []]]] -> [1, [2, 3, [4, 5], 6]]
	return [h[ID], [] if len(progenitors) == 0 else \
		[build(log, progenitor, data) for progenitor in progenitors]]

def flatten(tree):
	"""Finds all ``nodeIndex`` values belonging to a given merger tree
	
	Arguments:
		tree (list): merger tree generated by :func:`build`
	Returns:
		generator: to be fed as an argument to the ``list()`` function
	**References:**
		https://stackoverflow.com/a/2158532
	"""
	for node in tree:
		try:
			for subnode in flatten(node):
				yield subnode
		except:
			yield node

def mah(tree, progs, data, m0, nfw_f):
	"""Calculates mass assembly history from a given merger tree
	
	Arguments:
		tree (list): merger tree, generated by :func:`tree`
		progs (numpy.ndarray): all prigenitors of the root halo in a merger tree
			(effectively a flattened tree), calculated by :func:`flatten`, a subset of ``data``
		data (numpy.ndarray): dataset provided by :mod:`src.read` module
		m0 (int): mass of the root halo
		nfw_f (float): NFW :math:`f` parameter
	Returns:
		numpy.ndarray: MAH with rows formatted like ``[nodeIndex, snapshotNumber, sum(particleNumber)]``
	"""
	mah = []
	root = halo.get(tree[0], progs)

	for snap in np.unique(progs[:,SNAP]):
		sum_m = 0
		for h in progs[np.where(progs[:,SNAP] == snap)]:
			m = halo.mass(h, data)
			if m > nfw_f*m0:
				sum_m += m
		mah.append([root[ID], snap, sum_m])
	return np.array(mah)

if __name__ == '__main__':
	fileConfig("./logging.conf")
	log = logging.getLogger()

	with open("./output/ids.txt") as file_ids:
		for i, line in enumerate(file_ids):
			if i == int(sys.argv[1])-1:
				root = int(line)
	
	d = read.retrieve()
	h = halo.get(root, d)

	nfw_f = 0.01
	m0 = halo.mass(h, d)

	log.info("Found halo %d of mass %d at snapshot %d"%(root, m0, h[SNAP]))

	t = build(log, h, d)
	p = np.array([halo.get(id, d) for id in list(flatten(t))])
	m = mah(t, p, d, m0, nfw_f)

	log.info("Built a tree rooted at halo %d with %d progenitors"%(root, np.shape(p)[0]))

	with open("./output/mah.tsv", 'a') as file_tsv:
		for row in m:
			file_tsv.write("%d\t%02d\t%d\n"%(row[0], row[1], row[2]))

	log.info("Appended MAH of %d to %s"%(h[ID], "./output/mah.tsv"))

	# with open("./output/mah_%d.dot"%(root), 'w') as file_dot:
	# 	file_dot.write("digraph merger_tree { rankdir=BT;\n")
	# 	dot.tree(file_dot, t, d, m0, nfw_f)
	# 	file_dot.write("\tsubgraph snapshots {\n")
	# 	dot.mah(file_dot, m, p)
	# 	file_dot.write("\t}\n")
	# 	file_dot.write("}\n")

	# log.info("Wrote Dot graph to ./output/mah_%d.dot"%(root))

