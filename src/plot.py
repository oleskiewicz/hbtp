#!/usr/bin/env python
import sys, numpy as np
import read

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



	d:
		dataset; NumPy array with 6 columns, provided by ``read`` module
	h:
		halo; node of the tree progenitors of which are being queried
	visited_halo_ids:
		array of nodes whose histories have alreade been traversed; prevents
		duplicate runs deep inside the tree
	m0:
		main progenitors' mass
	f:
		NFW ``f`` parameter
	"""

	if h[0] != h[4]:
		raise Error("FATAL: not a host halo!")
		sys.exit(1)

	visited_halo_links.append(h[0])

	# node: "id (mass@snapshot)"
	m = h[3]
	f.write("\t%d [label=\"%d (%d@%d)\", style=filled, fillcolor=%s];\n"\
		%(h[0], h[0], m, h[2], 'green' if m > 0.01*m0 else 'red'))

	# query for all progenitors' hosts' ids, and keep unique ones
	for prog_host_id in np.unique(d[np.where(d[:,1] == h[0])][:,4]):
		f.write("\t%d -> %d;\n"%(prog_host_id, h[0]))
		if prog_host_id not in visited_halo_links:
			mah(d, d[np.where(d[:,0] == prog_host_id)][0], visited_halo_links, m0, f)

def main():

	# # MOCK
	# d = read.mock(data_frame=True)
	# with open(sys.argv[1], 'w') as f:
	# 	f.write("digraph { rankdir=BT\n")
	# 	full_tree(d, f)
	# 	f.write("}\n")

	# REAL
	d = read.data()
	h = d[np.where(d[:,0] == int(sys.argv[1]))][0] # 
	with open(sys.argv[2], 'w') as f:
		f.write("digraph { rankdir=BT\n")
		mah(d, h, [], h[3], f)
		f.write("}\n")

if __name__ == '__main__':
	main()

