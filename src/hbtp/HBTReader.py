#!/usr/bin/env python
import sys
import glob
import numbers
import numpy as np
import h5py
from numpy.lib.recfunctions import append_fields
from matplotlib.pylab import find

import logging
from logging.config import fileConfig
fileConfig("./log.conf")
log = logging.getLogger()

def PeriodicDistance(x,y, BoxSize, axis=-1):
	d=x-y
	d[d>BoxSize/2]=d[d>BoxSize/2]-BoxSize
	d[d<-BoxSize/2]=d[d<-BoxSize/2]+BoxSize
	return np.sqrt(np.sum(d**2, axis=axis))

def distance(x,y, axis=1):
	return np.sqrt(np.sum((x-y)**2, axis=axis))

def get_hbt_snapnum(snapname):
	return int(snapname.rsplit('SubSnap_')[1].split('.')[0])
			
class ConfigReader:
	"""Class to read the config files (i.e. Parameters.log)"""
	def __init__(self, config_file):
		self.Options={}
		with open(config_file, 'r') as f:
			for line in f:
				pair=line.lstrip().split("#",1)[0].split("[",1)[0].split()
				if len(pair)==2:
					self.Options[pair[0]]=pair[1]
				elif len(pair)>2:
					self.Options[pair[0]]=pair[1:]
	def __getitem__(self, index):
		return self.Options[index]

class HBTReader:
	"""Class to read the HBT outputs

	To use it, initialize the reader with the directory in which Parameters.log
	is stored.

	Arguments:
		subhalo_path (str): directory with config files
	"""
		
	def __init__(self, subhalo_path):
		config_file=subhalo_path+'/Parameters.log'
		self.Options=ConfigReader(config_file).Options
		self.rootdir=self.Options['SubhaloPath']
		self.MaxSnap=int(self.Options['MaxSnapshotIndex'])
		self.BoxSize=float(self.Options['BoxSize'])
		self.Softening=float(self.Options['SofteningHalo'])

		try:
			lastfile=sorted(glob.glob(self.rootdir+'/SubSnap_*.hdf5'), key=get_hbt_snapnum)[-1]
		except:
			lastfile=sorted(glob.glob(self.rootdir+'/*/SubSnap_*.hdf5'), key=get_hbt_snapnum)[-1]

		extension=lastfile.rsplit('SubSnap_')[1].split('.')
		MaxSnap=int(extension[0])

		if MaxSnap!=self.MaxSnap:
			log.info("HBT run not finished yet, maxsnap %d found (expecting %d)"\
				%(MaxSnap, self.MaxSnap))
			self.MaxSnap=MaxSnap

		self.nfiles=0
		if len(extension)==3:
			self.nfiles=len(glob.glob(self.rootdir+'/%03d'%MaxSnap+'/SubSnap_%03d.*.hdf5'%MaxSnap))
			log.info(self.nfiles, "subfiles per snapshot")

		if 'MinSnapshotIndex' in self.Options:
			self.MinSnap=int(self.Options['MinSnapshotIndex'])
		else:
			self.MinSnap=0
			
		try:
			with self.Open(-1) as f:
				self.ParticleMass=f['/Cosmology/ParticleMass'][0]
		except:
			log.error("fail to get ParticleMass.")
			pass

	def Snapshots(self):
		return np.arange(self.MinSnap, self.MaxSnap+1)
	
	def GetFileName(self, isnap, ifile=0, filetype='Sub'):
		"""Returns filename of an HBT snapshot
		
		Arguments:
			isnap (int): snapshot of the file
			ifile (int): (default=0) index for sub-snapshots
			filetype (str): (default='Sub') 'Src', 'Sub' or 'HaloSize'
		"""
		if isnap<0:
			isnap=self.MaxSnap+1+isnap
		if self.nfiles:
			return self.rootdir+'/%03d/'%isnap+filetype+'Snap_%03d.%d.hdf5'%(isnap, ifile)
		else:
			if filetype == 'HaloSize':
				return self.rootdir+'%s/%s_%03d.hdf5'%(filetype, filetype, isnap)
			else:
				return self.rootdir+'/'+filetype+'Snap_%03d.hdf5'%(isnap)

	def Open(self, isnap, ifile=0, filetype='Sub', mode='r'):
		"""Returns opened HDF5 file handle"""
		return h5py.File(self.GetFileName(isnap, ifile, filetype), mode)
	
	def LoadNestedSubhalos(self, isnap=-1):
		"""Load the list of nested subhalo indices for each subhalo

		Arguments:
			isnap (int): (default = -1) snapshot number
		"""
		nests=[]
		for i in xrange(max(self.nfiles,1)):
			with self.Open(isnap, i) as subfile:
				nests.extend(subfile['NestedSubhalos'][...])
		return np.array(nests)

	def LoadSubhalos(self, isnap=-1, selection=None, show_progress=False):
		"""Load all subhaloes from a snapshot

		.. Note::

			``selection=('Rank', 'Nbound')`` will load only the Rank and Nbound fields
			of subhaloes; ``selection=3`` will only load subhalo with subindex 3;
			default will load all fields of all subhaloes.  You can also use numpy
			slice for selection, e.g. ``selection=np.s_[:10, 'Rank','HostHaloId']``
			will select the ``Rank`` and ``HostHaloId`` of the first 10 subhaloes. You
			can also specify multiple subhaloes by passing a list of (ordered)
			subindex, e.g., ``selection=((1,2,3),)``.  However, currently only a
			single subhalo can be specified for multiple-file HBT data (not restricted
			for single-file data).

		.. Note::

			Subindex specifies the order of the subhalo in the file at the current
			snapshot, i.e., ``subhalo=AllSubhalo[subindex]``.  ``subindex == trackId``
			for single file output, but ``subindex != trackId`` for mpi multiple-file
			outputs. 

		Arguments:
			isnap (int): (default = -1) snapshot
			selection (numpy.s\_): (default = None) can be a single field, a list of
				the field names or a single subhalo index
			show_progress (bool): (default = False)
		"""""

		subhalos=[]
		offset=0
		trans_index=False
		if selection is None:
			selection=np.s_[:]
		else:
			trans_index=isinstance(selection, numbers.Integral)
		if type(selection) is list:
			selection=tuple(selection)

		for i in xrange(max(self.nfiles,1)):
			if show_progress:
				sys.stdout.write(".")
				sys.stdout.flush()
			# with h5py.File(self.GetFileName(isnap, i), 'r') as subfile:
			with self.Open(isnap, i) as subfile:
				nsub=subfile['Subhalos'].shape[0]
				if nsub==0:
					continue
				if trans_index:
					if offset+nsub>selection:
						subhalos.append(subfile['Subhalos'][selection-offset])
						break
					offset+=nsub
				else:
					subhalos.append(subfile['Subhalos'][selection])

		if len(subhalos):		
			subhalos=np.hstack(subhalos)
		else:
			subhalos=np.array(subhalos)
		# subhalos.sort(order=['HostHaloId','Nbound'])

		return subhalos

	def GetNumberOfSubhalos(self, isnap=-1):
		"""Retunrs number of subhaloes in a snapshot
		
		Arguments:
			isnap (int): (default = -1)
		"""
		with h5py.File(self.GetFileName(isnap, 0),'r') as f:
			if self.nfiles:
				return f['TotalNumberOfSubhalosInAllFiles'][...]
			else:
				return f['Subhalos'].shape[0]
				
	def LoadParticles(self, isnap=-1, subindex=None, filetype='Sub'):		
		"""Loads subhalo particle list at snapshot
		
		if subindex is given, only load subhalo of the given index (the order it
		appears in the file, subindex==trackId for single file output, but not for
		mpi multiple-file outputs). otherwise load all the subhaloes.
		
		default filetype='Sub' will load subhalo particles. set filetype='Src' to
		load source subhalo particles instead (for debugging purpose only).
		"""""

		subhalos=[]
		offset=0
		for i in xrange(max(self.nfiles,1)):
			with h5py.File(self.GetFileName(isnap,	i, filetype), 'r') as subfile:
				if subindex is None:
					subhalos.append(subfile[filetype+'haloParticles'][...])
				else:
					nsub=subfile[filetype+'haloParticles'].shape[0]
					if offset+nsub>subindex:
						subhalos.append(subfile[filetype+'haloParticles'][subindex-offset])
						break
					offset+=nsub
		subhalos=np.hstack(subhalos)
		return subhalos

	def GetParticleProperties(self, subindex, isnap=-1):		
		"""Returns subhalo particle properties for subhalo with index subindex (the
		order it appears in the file, subindex==trackId for single file output, but
		not for mpi multiple-file outputs)"""

		offset=0
		for i in xrange(max(self.nfiles,1)):
			with h5py.File(self.GetFileName(isnap,	i), 'r') as subfile:
				nsub=subfile['Subhalos'].shape[0]
				if offset+nsub>subindex:
					try:
						return subfile['ParticleProperties/Sub%d'%(subindex-offset)][...] #for compatibility with old data
					except: 
						return subfile['ParticleProperties'][subindex-offset]
				offset+=nsub
		raise RuntimeError("subhalo %d not found"%subindex)

	def GetSub(self, trackId, isnap=-1):
		"""Loads a subhalo with the given ``trackId`` at snapshot ``isnap``"""
		#subhalos=LoadSubhalos(isnap, rootdir)
		#return subhalos[subhalos['TrackId']==trackId]
		if self.nfiles:
			subid=find(self.LoadSubhalos(isnap, 'TrackId')==trackId)[0]
		else:
			subid=trackId
		return self.LoadSubhalos(isnap, subid)

	def GetTrack(self, trackId, MinSnap=None, MaxSnap=None, fields=None):
		"""Loads an entire track of the given ``trackId``"""
		track=[]
		snaps=[]
		MinSnap = self.GetSub(trackId)['SnapshotIndexOfBirth']\
			if MinSnap is None else MinSnap
		MaxSnap = self.MaxSnap if MaxSnap is None else MaxSnap
		for isnap in range(MinSnap, MaxSnap+1):
			s=self.GetSub(trackId, isnap)
			if fields is not None:
				s=s[fields]
			track.append(s)
			snaps.append(isnap)
		return append_fields(np.array(track), 'Snapshot', np.array(snaps), usemask=False)

	def GetScaleFactor(self, isnap):
		try:
			return h5py.File(self.GetFileName(isnap),'r')['Cosmology/ScaleFactor'][0]
		except:
			raise IndexError("HDF5 file structure does not have 'Cosmology/ScaleFactor' key")

	def GetExclusiveParticles(self, isnap=-1):
		"""Loads an exclusive set of particles for subhaloes at ``isnap``
		
		Duplicate particles are assigned to the lowest mass subhaloes.
		"""
		OriginPart=self.LoadParticles(isnap)
		OriginPart=zip(range(len(OriginPart)),OriginPart)
		comp_mass=lambda x: len(x[1])
		OriginPart.sort(key=comp_mass)
		repo=set()
		NewPart=[]
		for i,p in OriginPart:
			if len(p)>1:
				p=set(p)
				p.difference_update(repo)
				repo.update(p)
			NewPart.append((i,list(p)))
		comp_id=lambda x: x[0]
		NewPart.sort(key=comp_id)
		NewPart=[x[1] for x in NewPart]
		return NewPart

	def LoadHostHalos(self, isnap=-1, selection=None):
		"""Returns spatial properties of FoF groups for a snapshot"""

		hosthalos = []
		offset = 0
		trans_index = False
		if selection is None:
			selection = np.s_[:]
		else:
			trans_index = isinstance(selection, numbers.Integral)
		if type(selection) is list:
			selection = tuple(selection)

		with self.Open(isnap, filetype="HaloSize") as hostfile:
			nsub = hostfile['HostHalos'].shape[0]
			if trans_index:
				if offset + nsub > selection:
					try:
						hosthalos.append(hostfile['HostHalos'][selection - offset])
					except ValueError:
						pass
				offset += nsub
			else:
				try:
					hosthalos.append(hostfile['HostHalos'][selection])
				except ValueError:
					pass

		if len(hosthalos):		
			hosthalos = np.hstack(hosthalos)
		else:
			hosthalos = np.array(hosthalos)

		return hosthalos

	def GetHostHalo(self, HostHaloId, isnap=-1):
		"""Returns spatial information of a specific FoF group"""
		return self.LoadHostHalos(isnap, HostHaloId)[0]

	def GetSubsOfHost(self, HostHaloId, isnap=-1):
		"""Loads all subhaloes belonging to a host halo
		
		Uses information stored in ``Membership/GroupedTrackIds``.

		Arguments:
			HostHaloId (int): row number
			isnap (int): (default = -1)
		Returns:
			array of ``TrackIds`` (or empty array if FoF is empty)
		"""
		with self.Open(isnap) as subfile:
			trackIds = subfile['Membership/GroupedTrackIds'][HostHaloId]

		try:
			result = np.hstack([self.GetSub(trackId, isnap) for trackId in trackIds])
		except ValueError:
			result = []
		return result

	def GetMergerTree(self, HostHaloId, isnap=-1, file=None):
		"""Builds a FOF merger tree starting at a host halo ID
		
		Prints a Dot-ready digraph.

		Arguments:
			HostHaloId (int): a halo at which to root a tree
			isnap (int): (default = -1)
			file (File): (default=None) if not ``None``, Dot diagram will be generated
				on the fly
		Returns:
			(list): multiply embedded list with a tree, i.e. ``[1, [2, 3]]``
		"""
		progenitors = self.GetHostProgenitors(HostHaloId, isnap)

		log.debug("Halo %d at %d with %d progenitor(s)"\
			%(HostHaloId, isnap, len(progenitors)))

		if file is not None:
			file.write("\t\"%d_%d\" [label=\"%d, %d\"];\n"%\
				(isnap, HostHaloId, isnap, HostHaloId))
			for progenitor in progenitors:
				file.write("\t\"%d_%d\" -> \"%d_%d\";\n"%\
					(isnap, HostHaloId, isnap-1, progenitor))

		return [(HostHaloId, isnap), []\
			if len(progenitors) == 0 else\
			[self.GetMergerTree(progenitor, isnap-1, file)\
			for progenitor in progenitors]]

	def GetHostProgenitors(self, HostHaloId, isnap=-1):
		try:
			subhaloes = self.GetSubsOfHost(HostHaloId, isnap=isnap)['TrackId']
			result = np.unique([self.GetSub(subhalo, isnap=isnap-1)[0]['HostHaloId']\
				for subhalo in subhaloes\
				if self.GetSub(subhalo, isnap=isnap-1)[0]['Rank'] == 0])
		except:
			result = []
		finally:
			return result

	def GetCollapsedMassHistory(self, HostHaloId, isnap=-1, NFW_f=0.01):
		"""Calculates a CMH, starting at a FOF group
		
		CMH is a sum of masses of all progenitors over a threshold

		Arguments:
			HostHaloId (int): starting point of the tree
			isnap (int): (default = -1) initial snapshot
			NFW_f (float): (default = 0.01) NFW :math:`f` parameter
		"""
		#TODO: eliminate non-centrals
		m0 = self.GetHostHalo(HostHaloId, isnap)['M200Crit']
		trackIds = self.GetSubsOfHost(HostHaloId, isnap)['TrackId']

		log.info("Starting halo %d of mass %.2f with %d tracks at snapshot %d"\
			%(HostHaloId,m0,len(trackIds),isnap))

		hosts = []
		for trackId in trackIds:
			track = self.GetTrack(trackId, MaxSnap=isnap)
			log.debug("Track %d of halo %d@%d across %d snapshots"\
				%(trackId,HostHaloId,isnap,len(track)))
			hosts_of_track = zip(track['Snapshot'], track['HostHaloId'])
			hosts.extend(hosts_of_track)
		hosts = np.unique(np.array(hosts,\
			dtype=np.dtype([('Snapshot', int), ('HaloId', int)])), axis=0)
		hosts = hosts[hosts['HaloId'] != 0]
		ms = [self.GetHostHalo(host['HaloId'], host['Snapshot'])['M200Crit']\
			for host in hosts]
		hosts = append_fields(hosts, 'M200Crit', ms, usemask=False)
		snaps = np.unique(hosts['Snapshot'])

		log.info("Finished queries for halo %d@%d with %d host haloes across %d snapshots"\
			%(HostHaloId,isnap,len(hosts),len(snaps)))

		cmh = np.array(zip(\
			np.full(len(snaps), HostHaloId),\
			snaps,\
			np.zeros(len(snaps))),\
			dtype=np.dtype([\
				('HaloId',np.int32),\
				('Snapshot',np.int32),\
				('M200Crit',np.float32),\
			]))

		for i,_ in np.ndenumerate(cmh):
			cmh[i]['M200Crit'] = np.sum(filter(lambda m: m > NFW_f*m0,\
				hosts[hosts['Snapshot'] == cmh[i]['Snapshot']]['M200Crit']))

		log.info("Finished CMH for halo %d@%d"\
			%(HostHaloId,isnap))

		return cmh

	def GetHostProfile(self, selection=None, isnap=-1):
		"""Returns normalised, binned particle positions of a FoF group"""
		log.info('Retrieving profile for halos %s'%str(selection))
		profile = self.LoadHostHalos(isnap, selection)['Profile']
		return profile

	def CalculateProfile(self, TrackId, isnap=-1, bins=None):
		"""Returns normalised, binned particle positions of a subhalo"""
		result = []
		subhalo = self.GetSub(TrackId, isnap)
		positions = (self.GetParticleProperties(TrackId, isnap)['ComovingPosition']\
			- subhalo['ComovingAveragePosition'][0])\
			/ subhalo['BoundR200CritComoving']

		if bins is not None:
			distances = map(lambda row: np.sqrt(np.sum(map(lambda x: x*x, row))),\
				positions)
			result = np.histogram(distances, bins=bins)
		else:
			result = positions

		return result

	def CalculateHostProfile(self, HostHaloId, isnap=-1, bins=None):
		"""Returns normalised, binned particle positions of a FoF group"""
		log.debug('Calculating profile for halo %d'%HostHaloId)
		result = []

		try:
			subhalos = self.GetSubsOfHost(HostHaloId, isnap)['TrackId']
			hosthalo = self.LoadHostHalos(isnap, selection=HostHaloId)

			log.debug('Found %d subhalos'%len(subhalos))

			positions = [((particle - hosthalo['CenterComoving'])\
				/ hosthalo['R200CritComoving'])[0]\
				for subhalo in subhalos for particle in\
				self.GetParticleProperties(subhalo, isnap)['ComovingPosition']]
			
			log.debug('Found %d particles'%len(positions))

			if bins is not None:
				distances = np.apply_along_axis(lambda x:\
					np.sqrt(np.sum(np.power(x, 2.0))), 1, positions)
				result = np.histogram(distances, bins=bins)
			else:
				result = positions

		except TypeError:
			result = []

		return result
