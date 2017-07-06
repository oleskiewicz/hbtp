#!/usr/bin/env python
import sys
import numpy as np

from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG, columns
import read
import halo

def yaml_from_tree(t, properties, level=1):
	tab = "  "
	ind = tab*level
	for h in t:
		sys.stdout.write("%s- "%(tab*(level-1)))
		print "root: %d"%(h['root'])
		for property in properties:
			print "%s%s: %s"%(ind, columns[property], str(h['properties'][columns[property]]))
		if len(h['children']) > 0:
			print "%schildren:"%(ind)
			yaml_from_tree(h['children'], properties, level=level+1)
		else:
			print "%schildren: None"%(ind)

def full_tree(d, f):
	"""Naive, full--tree plot.

	Arguments:
		d (pandas.DataFrame): dataset provided by :mod:`src.read` module
		f (File): graphviz ``.dot`` file to output
	"""

	for i in d['nodeIndex']:
		desc = d['descendantIndex'][i]

		if desc == -1:
			f.write("\t%d;\n"%(i))
		else:
			f.write("\t%d -> %d;\n"%(i, desc))
		f.write("\t%d [label=\"%d (%d)\"];\n"%(i, i, d['particleNumber'][i]))

		haloes_in_snapshot = d.groupby('snapshotNumber')['nodeIndex'].apply(list)
		masses_in_snapshot = d.groupby('snapshotNumber')['particleNumber'].apply(list)

		for i,_ in enumerate(haloes_in_snapshot):
			rank_label = "\tsnap_%03d [label=\"s_%d (%d)\"];"\
				%(haloes_in_snapshot.index[i], \
					haloes_in_snapshot.index[i], \
					sum(masses_in_snapshot.iloc[i]))
			rank_label += "\t{rank=same; snap_%03d; "%(haloes_in_snapshot.index[i])
			for node in haloes_in_snapshot.iloc[i]:
				rank_label += str(node)+"; "
			f.write("%s};\n"%rank_label)

def dot_from_data(h, d, mah, m0, f=0.01):
	"""Recursive mass assembly history.

	Arguments:
		d (numpy.ndarray): dataset provided by :mod:`src.read` module
		h (numpy.ndarray): halo; node of the tree progenitors of which are being queried
		m0 (int): main progenitors' mass
		f (float): NFW :math:`f` parameter
	"""

	if not halo.is_main(h, d): raise ValueError("Not a host halo!")

	print "\t%d [label=\"%d (%d, %d, %d)\", style=filled, fillcolor=%s];\n"\
		%(h[ID], h[ID], h[MAIN_PROG], h[MASS], h[SNAP], \
		'green' if h[DESC_HOST] == h[DESC] else 'red')

	progs = halo.progenitors(h, d)
	if (len(progs) > 0):
		for prog in progs:
			print "\t%d -> %d;\n"%(prog, h[ID])
			dot_from_data(halo.get(prog, d), d, mah, m0, f)

def yaml_from_data(h, d, m0, level=1, recursive=False):
	"""Display information about halo ``h`` in a tree structure.

	- can be used recursively or not
	- exports data in a YAML format

	Arguments:
		h (int): ``nodeIndex`` queried
		d (numpy.ndarray): DHalo tree data, as provided by :mod:`src.read`
		level (int): (default=1) used to increase level counter if printed
			recursively
		recursive (bool): (default=False) if ``True``, descends every time a foreign
			key is encountered;  if ``False``, only prints the IDs
	"""

	if not halo.is_main(h, d): raise ValueError("Not a host halo!")

	h = halo.get(h, d)
	tab = "  "
	ind = tab*level

	# HALO
	sys.stdout.write("%s- "%(tab*(level-1)))
	print "halo: %d"%(h[ID])
	print "%ssnap: %d"%(ind, h[SNAP])
	print "%smass: %.3f"%(ind, float(h[MASS])/float(m0))
	print "%smain: %s"%(ind, "True" if h[DESC_HOST] == h[DESC] else "False")

	# DESCENDANTS
	print "%sdesc: %d"%(ind, h[DESC])
	print "%sdesc_host: %d"%(ind, h[DESC_HOST])

	# # HOST
	# print "%shost: %s"%(ind, "self" if h[ID] == h[HOST] else str(h[HOST]))

	# PROGENITORS
	hh = halo.progenitors(h, d)
	if (len(hh) > 0):
		if recursive:
			print "%sprog:"%(ind)
			for _h in hh:
				yaml_from_data(_h, d, m0, level+1, True)
		else:
			print "%sprog: [%s]"%(ind, ",".join(map(str, hh)))
	else:
		print "%sprog: -1"%(ind)

def tree_from_data(h, d, props):
	if not halo.is_main(h, d): raise ValueError("Not a main halo")

	h = halo.get(h, d)
	progs = list(halo.progenitors(h, d))

	return [{
		'root': h[ID],
		'properties': {} if len(props) == 0 else {read.columns[prop]: h[prop] for prop in props},
		'children': [] if len(progs) == 0 else [tree_from_data(prog, d, props)[0] for prog in progs],
	},]

def dot_from_tree(t):
	for h in t:
		print "\t%d [label=\"%d (%d, %d, %d)\", style=filled, fillcolor=%s];"%(\
			h['root'], h['root'], h['properties']['isMainProgenitor'], h['properties']['particleNumber'], \
			h['properties']['snapshotNumber'], \
			"green" if h['properties']['descendantIndex'] == h['properties']['descendantHost']  else "red")
		if len(h['children']) > 0:
			for prog in h['children']:
				print "\t%d -> %d;"%(prog['root'], h['root'])
			dot_from_tree(h['children'])

def mah_from_tree(t, d, f=0.01):
	"""Naive, slow implementation of group-by for all progenitors
	"""
	progs = np.array([halo.get(id, d) for id in \
		list(halo.all_progenitors(t[0], 'root'))])
	m0 = t[0]['properties']['particleNumber']
	mah = []
	for snap in np.unique(progs[:,SNAP]):
		m = 0
		for prog in progs[np.where(progs[:,SNAP] == snap)]:
			if prog[MASS] > f*m0:
				m += prog[MASS]
		mah.append([snap, m])
	return np.array(mah)

if __name__ == '__main__':
	d = read.retrieve()
	h = halo.get(int(sys.argv[1]), d)

	t = tree_from_data(h, d, [MASS, SNAP, MAIN_PROG, DESC, DESC_HOST])
	mah = mah_from_tree(t, d, 0.1)
