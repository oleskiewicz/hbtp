#!/usr/bin/env python
import sys
import numpy as np
import pandas as pd

from src import process

def snaps():
	d = np.genfromtxt("./output/hbtp/redshift_list.txt", delimiter=" ",\
		dtype=np.dtype([('Snapshot', np.int32), ('Redshift', np.float32)]))
	return d

def prop(snap):
	d = pd.read_csv("./output/hbtp/prop_%03d.csv"%snap)
	# param['rhos'] = (param['rhos']*h*h*ParticleMass)/Rho0/rho_crit(z0) #TODO: normalisation
	d['mass_bin'] = process.bin(d, 'M200Crit',\
		bins=np.linspace(9.0, 14.5, 11),\
		transform=lambda m: np.log10(m*1.52e11))
	return d

def prof(snap):
	d = pd.read_csv("./output/hbtp/prof_%03d.csv"%snap)
	d.set_index('HostHaloId', inplace = True)
	d.fillna(0.0, inplace = True)
	return d

def cmh(snap):
	d = pd.read_csv("./output/hbtp/cmh_%03d.csv"%snap)
	d.set_index(['HostHaloId', 'IdentificationSnapshot'], inplace = True)
	d.fillna(0.0, inplace = True)
	return d
