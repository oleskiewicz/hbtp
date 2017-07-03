#!/usr/bin/env python
import sys, numpy as np
import read
from read import ID, DESC, SNAP, MASS, HOST, DESC_HOST, MAIN_PROG

def full_tree(d, f):
	"""
	Naive, full-tree plot
	"""
	for i in d['nodeIndex']:
		desc = d['descendantIndex'][i]
		m = d['particleNumber'][i]

		if desc == -1:
			f.write("\t%d;\n"%(i))
		else:
			f.write("\t%d -> %d;\n"%(i, desc))
		f.write("\t%d [label=\"%d (%d)\"];\n"%(i, i, m))

		h_s = d.groupby('snapshotNumber')['nodeIndex'].apply(list)
		m_s = d.groupby('snapshotNumber')['particleNumber'].apply(list)

		for i,_ in enumerate(h_s):
			rank_label = "\tsnap_%03d [label=\"s_%d (%d)\"];"%(h_s.index[i], h_s.index[i], sum(m_s.iloc[i]))
			rank_label += "\t{rank=same; snap_%03d; "%(h_s.index[i])
			for node in h_s.iloc[i]:
				rank_label += str(node)+"; "
			f.write("%s};\n"%rank_label)

def mah(d, h, visited_halo_links, m0, f):
	"""Recursive mass assembly history.

	Arguments:
		d (numpy.ndarray): dataset provided by :mod:`src.read` module
		h (table row): halo; node of the tree progenitors of which are being queried
		m0 (int): main progenitors' mass
		f (float): NFW :math:`f` parameter
	"""

	#TODO: implement recursive host (keep going until sureyl host)
	# if h[ID] != h[HOST]:
	# 	raise Error("FATAL: not a host halo!")
	# 	sys.exit(1)

	m = h[MASS]
	f.write("\t%d [label=\"%d%s (%d:%d@%d)\", style=filled, fillcolor=%s];\n"\
		%(h[ID], h[ID], "" if h[HOST] == h[ID] else " < %s"%h[HOST], h[MAIN_PROG], \
		m, h[SNAP], 'green' if h[DESC_HOST] == h[DESC] else 'red'))

	progs = np.unique(d[np.where(d[:,DESC_HOST] == h[ID])][:,HOST])
	#TODO: check if not empty
	for prog in progs:
		if ([prog, h[ID]] not in visited_halo_links):
			visited_halo_links.append([prog, h[ID]])
			f.write("\t%d -> %d;\n"%(prog, h[ID]))
			mah(d, d[np.where(d[:,ID] == prog)][0], visited_halo_links, m0, f)

def main():
	d = read.retrieve()
	h = d[np.where(d[:,ID] == int(sys.argv[1]))][0] # 
	with open(sys.argv[2], 'w') as f:
		f.write("digraph { rankdir=BT;\n")
		mah(d, h, [], h[MASS], f)
		f.write("}\n")

if __name__ == '__main__':
	main()

