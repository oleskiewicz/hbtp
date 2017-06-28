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
	"""
	Recursive mass assembly history

 
	:param d: dataset provided by ``read`` module
	:type d: ``numpy.ndarray``
	:param h: halo; node of the tree progenitors of which are being queried
	:type h: table row
	:param m0: main progenitors' mass
	:type m0: ``int``
	:param f: NFW :math:`f` parameter
	:type f: ``float``
	"""

	if h[ID] != h[HOST]:
		raise Error("FATAL: not a host halo!")
		sys.exit(1)


	# node: "id (main_prog:mass@snapshot)"
	m = h[MASS]
	f.write("\t%d [label=\"%d (%d:%d@%d)\", style=filled, fillcolor=%s];\n"\
		%(h[ID], h[ID], h[MAIN_PROG], m, h[2], 'green' if m > 0.01*m0 else 'red'))

	# query for all progenitors' hosts' ids, and keep unique ones
	prog_host_ids = np.unique(d[np.where(d[:,DESC] == h[ID])][:,HOST])
	for prog_host_id in prog_host_ids:
		if ([prog_host_id, h[ID]] not in visited_halo_links and \
			  d[np.where(d[:,ID] == prog_host_id)][0][MAIN_PROG] == 1):
			visited_halo_links.append([prog_host_id, h[ID]])
			f.write("\t%d -> %d;\n"%(prog_host_id, h[ID]))
			mah(d, d[np.where(d[:,ID] == prog_host_id)][0], visited_halo_links, m0, f)

def main():
	d = read.retrieve()
	h = d[np.where(d[:,ID] == int(sys.argv[1]))][0] # 
	with open(sys.argv[2], 'w') as f:
		f.write("digraph { rankdir=BT\n")
		mah(d, h, [], h[MASS], f)
		f.write("}\n")

if __name__ == '__main__':
	main()

