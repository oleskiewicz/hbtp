#!/usr/bin/env python
import h5py, numpy as np, pandas as pd

filename = "./data/tree_063.0.hdf5"
columns = ['nodeIndex',\
           'descendantIndex',\
           'snapshotNumber',\
           'particleNumber',\
           'hostIndex',\
           'descendantHost',\
           'isMainProgenitor',\
					]
# column ids
ID        = 0
DESC      = 1
SNAP      = 2
MASS      = 3
HOST      = 4
DESC_HOST = 5
MAIN_PROG = 6

def mock(data_frame=False):
	d = np.array([[0,1,2,3,4,5,6,7,8,9], # nodeIndex
                [-1,0,1,1,3,3,-1,6,7,-1], # descendantIndex
                [4,3,2,2,1,1,4,3,2,2], # snapshotNumber
                [10,8,3,5,2,3,4,4,4,2]]).T # particleNumber
	if data_frame:
		d = pd.DataFrame(d, columns=columns[0:4])
	return d

def data(filename=filename, numpy_file="./output/data.np", data_frame=False):
	"""
	Function reading DHalo data.

	:param filename: HDF5 data store
	:type filename: str
	:param numpy_file: filename to which NumPy array object can be saved (for
	  faster re-reads); this is later used in :func:`src.read.retrieve`
	:type numpy_file: str
	:param data_frame: whether to return a DataFrame or not (default not, returns
	  NumPy array)
	:type data_frame: bool
	:return:  DHalo catalogue
	:rtype: numpy.ndarray / pandas.DataFrame

	**Output data format:**

	===========  ==================
	 Column ID    Column Name
	===========  ==================
	         0    nodeIndex        
	         1    descendantIndex  
	         2    snapshotNumber   
	         3    particleNumber   
	         4    hostIndex        
	         5    descendantHost   
	         6    isMainProgenitor 
	===========  ==================
	
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
	isMainProgenitor:
		1 if it is

	:Example:

	To retrieve a single halo, run

	.. code-block:: python

		d = read.data()
		h = d[np.where(d[:,ID] == 123)][0]
	"""
	f = h5py.File(filename, 'r')
	t = f['/haloTrees']
	if data_frame:
		d = pd.DataFrame({column: np.array(t[column].value) for column in columns})
		d.index = d.nodeIndex
	else:
		d = np.array([np.array(t[column].value) for column in columns]).T
		d[0] = np.array([0 for column in columns])
		if numpy_file is not None:
			with open(numpy_file, 'w') as numpy_file:
				np.save(numpy_file, d)
	f.close()
	return d

def retrieve(numpy_file="./output/data.np"):
	"""
	Retrieves NumPy object saved by :func:`src.read.data`
	"""
	return np.load(open(numpy_file, 'r'))

def main():
	print "%s:"%filename
	print data(data_frame=True).head()

if __name__ == '__main__':
	main()

