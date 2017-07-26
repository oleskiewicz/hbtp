#!/usr/bin/env python
import logging
from logging.config import fileConfig
import h5py
import numpy as np
import pandas as pd

hdf5_file  = "./data/tree_063.0.hdf5"
numpy_file = "./output/data.npy"

ID        = 0
DESC      = 1
SNAP      = 2
MASS      = 3
HOST      = 4
DESC_HOST = 5
MAIN_PROG = 6
columns = [\
	'nodeIndex',\
	'descendantIndex',\
	'snapshotNumber',\
	'particleNumber',\
	'hostIndex',\
	'descendantHost',\
	'isMainProgenitor',\
]

def mock(data_frame=False):
	"""Returns a tiny mock dataset

	Arguments:
		data_frame (bool): whether to return a DataFrame or NumPy array (default is
		NumPy array)
	Returns:
		numpy.ndarray / pandas.DataFrame: small dataset, suitable for testing
			algorithms in :mod:`src.tree`
	"""
	d = np.array([[ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],     # nodeIndex
                [-1, 0, 1, 1, 3, 3,-1, 6, 7, 1],     # descendantIndex
                [ 4, 3, 2, 2, 1, 1, 4, 3, 2, 2],     # snapshotNumber
                [10, 8, 3, 5, 2, 3, 4, 4, 4, 2]]).T  # particleNumber
	if data_frame:
		d = pd.DataFrame(d, columns=columns[0:4])
	return d

def data(hdf5_file, numpy_file=None, data_frame=False):
	"""Reads DHalo data into memory

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

	Arguments:
		hdf5_file (str): filename of an HDF5 data store
		numpy_file (str): filename to which NumPy array object can be saved (for
			faster re-reads);  this is later used for faster data retrieval in
			:func:`src.read.retrieve`;  if ``None``, no data is cached
		data_frame (bool): whether to return a DataFrame or not (default not, returns
			NumPy array)

	Returns:
		numpy.ndarray / pandas.DataFrame:  DHalo catalogue

	Example:
		To retrieve a single halo of ``nodeIndex=123``, run:

		.. code-block:: python

			d = read.data()
			h = d[np.where(d[:,ID] == 123)][0]
	"""

	f = h5py.File(hdf5_file, 'r')
	t = f['/haloTrees']

	d = np.array([np.array(t[column].value) for column in columns]).T
	d[0] = np.array([0 for column in columns])
	if numpy_file is not None:
		with open(numpy_file, 'w') as numpy_file:
			np.save(numpy_file, d)

	if data_frame:
		d = pd.DataFrame(d, columns=columns)
		d.index = d.nodeIndex
	
	f.close()
	return d

def retrieve(numpy_file=numpy_file):
	"""Loads data saved in a NumPy binary format instead of HDF5 catalogue, as
	provided by :func:`src.read.data`

	Arguments:
		numpy_file (str): source of NumPy binary store generated by
		  :func:`src.read.data`
	"""
	return np.load(open(numpy_file, 'r'))

if __name__ == '__main__':
	fileConfig("./logging.conf")
	log = logging.getLogger()
	log.info("Saving %s to %s"%(hdf5_file, numpy_file))
	d = data(hdf5_file, numpy_file, data_frame=True)
	print d.head()

