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
	"""
	Function reading DHalo data and returning NumPy object or Pandas DataFrame.

	Halo table format:
	
	nodeIndex:
		index of each halo or subhalo, unique across the entire catalogue
	descendantIndex:
		index of a descendanta halo (if multiple haloes have the same descendatant
		index, they all are the progenitors)
	snapshotNumber:
		snapshot at which halo was identified
	particleNumber:
		number of particles in a halo; might differ from masses identified by other
		methods
	hostIndex:
		index of a host halo; for subhaloes, this points to a parent halo; for main
		haloes, this points to themselves
	descendantHost:
		index of a host halo of descendant of a halo (or subhalo); this field
		eliminates "multiple descendance" problem, always creating a merger history
		which works for main progenitors only
	"""
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

