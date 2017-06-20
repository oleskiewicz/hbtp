#!/usr/bin/env python
import sys
import h5py, numpy as np, pandas as pd

# # ACTUAL DATA
# d = pd.DataFrame({'snapshotNumber': np.array(h['snapshotNumber'].value),\
# 									'descendantSnapshot': np.array(h['descendantSnapshot'].value),\
# 									'nodeIndex': np.array(h['nodeIndex'].value),\
# 									'particleNumber': np.array(h['particleNumber'].value),\
# 									'descendantIndex': np.array(h['descendantIndex'].value)})
# d.index = d.nodeIndex

# # SMALL DATA
# d = pd.DataFrame({'nodeIndex': np.array([0,1,2,3,4,5,6,7,8,9]),\
#                   'descendantIndex': np.array([-1,0,1,1,3,3,-1,6,7,-1]),\
# 	                'snapshotNumber': np.array([4,3,2,2,1,1,4,3,2,2]),\
# 									'particleNumber': np.array([10,8,3,5,2,3,4,4,4,2])})
# d.index = d.nodeIndex

# # NAIVE GRAPH - all nodes, ever
# print "digraph { rankdir=BT"
# for i in d['nodeIndex']:
# 	desc = d['descendantIndex'][i]
# 	m = d['particleNumber'][i]
# 	if desc == -1:
# 		print "\t%d;"%(i)
# 	else:
# 		print "\t%d -> %d;"%(i, desc)
# 	node_label = "\t%d [label=\"%d (%d)\"]"%(i, i, m)
# 	print node_label
# h_s = d.groupby('snapshotNumber')['nodeIndex'].apply(list)
# m_s = d.groupby('snapshotNumber')['particleNumber'].apply(list)
# for i,_ in enumerate(h_s):
# 	rank_label = "\tsnap_%03d [label=\"s_%d (%d)\"];"%(h_s.index[i], h_s.index[i], sum(m_s.iloc[i]))
# 	rank_label += "\t{rank=same; snap_%03d; "%(h_s.index[i])
# 	for node in h_s.iloc[i]:
# 		rank_label += str(node)+"; "
# 	print rank_label+"}"
# print "}"

d = np.array([[0,1,2,3,4,5,6,7,8,9],       # nodeIndex
              [-1,0,1,1,3,3,-1,6,7,-1],    # descendantIndex
              [4,3,2,2,1,1,4,3,2,2],       # snapshotNumber
              [10,8,3,5,2,3,4,4,4,2]]).T   # particleNumber

# f = h5py.File("./data/tree_063.0.hdf5", 'r')
# t = f['/haloTrees']
# d = np.array([\
# 	np.array(t['nodeIndex'].value[0:100]),\
# 	np.array(t['descendantIndex'].value[0:100]),\
# 	np.array(t['snapshotNumber'].value[0:100]),\
# 	np.array(t['particleNumber'].value[0:100]),\
# ]).T

# RECURSIVE GRAPH - starting from a selected node
def mah(h):
	if h[1] != -1:
		print "\t%d -> %d;"%(h[0], h[1])
	else:
		print "\t%d;"%(h[0])
	for desc in np.where(d[:,1] == h[0])[0]:
		mah(d[desc])

print "digraph { rankdir=BT"
mah(d[0])
print "}"

