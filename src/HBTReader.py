#!/usr/bin/env python
import numpy as np
import h5py
import sys
import os.path, glob
from numpy.lib.recfunctions import append_fields
from matplotlib.pylab import find
import numbers
import logging
from logging.config import fileConfig

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
			print "HBT run not finished yet, maxsnap %d found (expecting %d)"%(MaxSnap, self.MaxSnap)
			self.MaxSnap=MaxSnap

		self.nfiles=0
		if len(extension)==3:
			self.nfiles=len(glob.glob(self.rootdir+'/%03d'%MaxSnap+'/SubSnap_%03d.*.hdf5'%MaxSnap))
			print self.nfiles, "subfiles per snapshot"

		if 'MinSnapshotIndex' in self.Options:
			self.MinSnap=int(self.Options['MinSnapshotIndex'])
		else:
			self.MinSnap=0
			
		try:
			with self.Open(-1) as f:
				self.ParticleMass=f['/Cosmology/ParticleMass'][0]
		except:
			print "Info: fail to get ParticleMass."

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
				return "%s/%s/%s_%d.hdf5"%(self.rootdir, filetype, filetype, isnap)
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
			with h5py.File(self.GetFileName(isnap, i), 'r') as subfile:
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
		if show_progress:
			print ""
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

	def GetTrack(self, trackId, fields=None):
		"""Loads an entire track of the given ``trackId``"""
		track=[]
		snaps=[]
		snapbirth=self.GetSub(trackId)['SnapshotIndexOfBirth']
		for isnap in range(snapbirth, self.MaxSnap+1):
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

	def GetProfile(self, TrackId, isnap=-1):
		"""Returns normalised, binned particle positions of a subhalo"""
		subhalo = self.GetSub(TrackId, isnap)
		positions = (self.GetParticleProperties(TrackId, isnap)['ComovingPosition']\
			- subhalo['ComovingAveragePosition'][0])\
			/ subhalo['BoundR200CritComoving']
		distances = map(lambda row: np.sqrt(np.sum(map(lambda x: x*x, row))),\
			positions)
		return np.histogram(distances, bins=np.logspace(-2.5, 0.0, 32))

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

	def GetHaloSize(self, HostHaloId, isnap=-1):
		"""Returns spatial information of a specific FoF group"""
		HostHalos = self.LoadHostHalos(isnap)
		return HostHalos[HostHalos['HaloId'] == HostHalos]

	def GetSubsOfHost(self, HostHaloId, isnap=-1):
		"""Loads all subhaloes belonging to a host halo
		
		Uses information stored in ``Membership/GroupedTrackIds``.

		Arguments:
			HostHaloId (int): row number
			isnap (int): (default = -1)
		"""
		with self.Open(isnap) as subfile:
			trackIds = subfile['Membership/GroupedTrackIds'][HostHaloId]
		return np.hstack([self.GetSub(trackId, isnap) for trackId in trackIds])

	def GetMergerTree(self, file, log, HostHaloIds, KnownTracks, isnap=-1):
		"""Builds a FOF merger tree starting at a host halo ID
		
		Prints a Dot-ready digraph.

		Arguments:
			file (File): ``.dot`` output file 
			log (logging.Logger): log object
			HostHaloIds (list): originally a one-element list, recursively called to
				contain all progenitors at each snapshot
			isnap (int): (default = -1)
		"""
		if len(HostHaloIds) > 0:
			for HostHaloId in HostHaloIds:
				subhaloes = self.GetSubsOfHost(HostHaloId, isnap=isnap)
				try:
					log.info("{halo: %03d_%d, tracks: %s}"%\
						(isnap, HostHaloId, str(subhaloes['TrackId'])))

					previous_hosts = np.unique([self.GetSub(track, isnap=isnap-1)[0]['HostHaloId']\
						# for track in list(subhaloes['TrackId'])]) # all
						for track in list(subhaloes['TrackId']) if self.GetSub(track, isnap=isnap-1)[0]['Rank'] == 0]) # no non-central following
						# for track in list(subhaloes['TrackId']) if track in KnownTracks]) # no new tracks

					for PreviousHostHaloId in previous_hosts:
						file.write("\t%03d000%d -> %03d000%d;\n"%\
							(isnap, HostHaloId, isnap-1, PreviousHostHaloId))

					self.GetMergerTree(f, log, previous_hosts, KnownTracks, isnap-1)
				except:
					log.info("{halo: %03d_%d, NA}"%(isnap, HostHaloId))
				finally:
					file.write("\t%03d000%d [label=\"%d, %d, %d\"];\n"%\
						(isnap, HostHaloId, isnap, HostHaloId, len(subhaloes)))

if __name__ == '__main__':
	fileConfig("./logging.conf")
	l = logging.getLogger()

	host0, snap0 = int(sys.argv[1]), int(sys.argv[2])
	reader = HBTReader("./data/")

	print reader.LoadHostHalos(snap0, selection=host0)

	# # animation
	# subs = reader.GetSubsOfHost(host0, snap0)
	# track = subs[subs['Rank'] == 0][0]['TrackId']
	# print reader.GetProfile(track, snap0)[0]

	# Dot graph
	# with open("./output/hbt.dot", 'w') as f:
	# 	f.write("digraph {\n")
	# 	reader.GetMergerTree(f, l, [host0,], reader.GetSubsOfHost(host0, snap0)['TrackId'], snap0)
	# 	f.write("}\n")

