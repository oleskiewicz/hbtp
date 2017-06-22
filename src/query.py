#!/usr/bin/env python
import sys
import h5py, numpy as np, pandas as pd

# # REAL DATA - PANDAS
# d = pd.DataFrame({'snapshotNumber': np.array(h['snapshotNumber'].value),\
#									'descendantSnapshot': np.array(h['descendantSnapshot'].value),\
#									'nodeIndex': np.array(h['nodeIndex'].value),\
#									'particleNumber': np.array(h['particleNumber'].value),\
#									'descendantIndex': np.array(h['descendantIndex'].value)})
# d.index = d.nodeIndex

# # MOCK DATA - NUMPY
# d = np.array([[0,1,2,3,4,5,6,7,8,9],		 # nodeIndex
#				[-1,0,1,1,3,3,-1,6,7,-1],	 # descendantIndex
#				[4,3,2,2,1,1,4,3,2,2],		 # snapshotNumber
#				[10,8,3,5,2,3,4,4,4,2]]).T	 # particleNumber

# REAL DATA - NUMPY
f = h5py.File("./data/tree_063.0.hdf5", 'r')
t = f['/haloTrees']
d = np.array([\
	np.array(t['nodeIndex'].value),\
	np.array(t['descendantIndex'].value),\
	np.array(t['snapshotNumber'].value),\
	np.array(t['particleNumber'].value),\
	np.array(t['hostIndex'].value),\
	np.array(t['descendantHost'].value),\
]).T
f.close()

for id in [35048400001660, 36048400001731, 36048400001670, 37048400001615, 37048400000752]:
	print d[np.where(d[:,0] == id)][0]

