#!/usr/bin/env python
import sys
import pandas as pd

def forge(data):
	"""Un-melts (forges) the DataFrame from long format to a wide one

	In essence, we want to go from

	=========== ======================= ========= =========
	HostHaloId  IdentificationSnapshot  Snapshot  M200Crit
	=========== ======================= ========= =========
	1           122                     11        0
	1           122                     12        0
	1           122                     13        0
	1           122                     14        324
	1           122                     15        653
	1           122                     16        849
	1           122                     17        1204
	1           122                     ...       ...
	2           122                     10        0
	2           122                     11        0
	2           122                     12        0
	2           122                     13        0
	2           122                     14        0
	2           122                     15        132
	2           122                     16        661
	2           122                     17        945
	2           ...                     ...       ...
	...
	=========== ======================= ========= =========

	to

	=========== ======================= ==== ==== ==== ==== ==== ==== ==== ==== ====
	HostHaloId  IdentificationSnapshot  10   11   12   13   14   15   16   17   ...
	=========== ======================= ==== ==== ==== ==== ==== ==== ==== ==== ====
	1           122                     NA   0    0    0    324  653  849  1204 ...
	2           122                     0    0    0    0    0    132  661  945  ...
	...
	=========== ======================= ==== ==== ==== ==== ==== ==== ==== ==== ====

	as described in https://cran.r-project.org/web/packages/reshape2/reshape2.pdf

	Note:
		Because IDs in HBT+ change, each row in *wide* format corresponds to a halo
		of ``HaloId``, as identified at snapshot ``IdentificationSnapshot``
	Arguments:
		data (pandas.DataFrame): input CMH DataFrame in a long format, read from a
			TSV written by :mod:`src.hbtp.cmh`
	Returns:
		pandas.DataFrame: output CMH DataFrame in a wide format
	"""
	return data.pivot_table(\
		values='M200Crit',\
		columns='Snapshot',
		index=['HostHaloId', 'IdentificationSnapshot'])

if __name__ == '__main__':
	f = "./output/hbtp/cmh_%03d.csv"%(int(sys.argv[1]))
	long = pd.read_csv(f, sep=",")
	wide = forge(long)
	wide.to_csv(f, sep=",")

