#!/usr/bin/env python
import h5py, numpy as np, pandas as pd

filename = "./data/tree_063.0.hdf5"
columns = ['nodeIndex',\
           'descendantIndex',\
           'snapshotNumber',\
           'particleNumber',\
           'hostIndex',\
           'descendantHost',]

def mock(data_frame=False):
	d = np.array([[0,1,2,3,4,5,6,7,8,9], # nodeIndex
                [-1,0,1,1,3,3,-1,6,7,-1], # descendantIndex
                [4,3,2,2,1,1,4,3,2,2], # snapshotNumber
                [10,8,3,5,2,3,4,4,4,2]]).T # particleNumber
	if data_frame:
		d = pd.DataFrame(d, columns=columns[0:4])
	return d

def data(filename=filename, data_frame=False):
	f = h5py.File(filename, 'r')
	t = f['/haloTrees']
	if data_frame:
		d = pd.DataFrame({column: np.array(t[column].value) for column in columns})
		d.index = d.nodeIndex
	else:
		d = np.array([np.array(t[column].value) for column in columns]).T
	f.close()
	return d

def main():
	print "%s:"%filename
	print data(data_frame=True).head()

if __name__ == '__main__':
	main()

