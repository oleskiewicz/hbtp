#!/usr/bin/env python
import sys
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

from src.hbtp.HBTReader import HBTReader
from src import process

if __name__ == '__main__':
	snap = int(sys.argv[1])
	host = int(sys.argv[2])
	reader = HBTReader("./data/")
	hosthalo = reader.LoadHostHalos(snap, selection=host)

	fig = plt.figure()#figsize=plt.figaspect(0.5))
	fig.suptitle("FoF group %d at snapshot %d"%(host, snap))

	# left panel - 3D partile positions
	ax = fig.add_subplot(1, 1, 1, projection='3d')

	ax.set_xlim3d([-5,5])
	ax.set_ylim3d([-5,5])
	ax.set_zlim3d([-5,5])

	ax.view_init(30, 2*snap)

	for trackId in reader.GetSubsOfHost(host, snap)['TrackId']:
		positions = (reader.GetParticleProperties(trackId, snap)['ComovingPosition']\
			- hosthalo['CenterComoving']) / hosthalo['R200CritComoving']
		ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2])

	# # right panel - density profile
	# ax = fig.add_subplot(1, 2, 2)

	# ax.set_xlabel("r")
	# ax.set_ylabel("differential mass")
	# ax.set_xlim([-2.75, 0.25])
	# ax.set_ylim([-4.1, 0.1])

	# prof, edges = reader.GetHostProfile(host, snap, bins=np.logspace(-2.5, 0.0, 33))
	# prof = np.array(prof, dtype=np.float32)
	# prof = np.cumsum(prof)
	# prof = np.log10(np.divide(prof, prof[-1]))
	# prof = process.normalise(prof)

	# ax.plot(edges[1:], prof)

	# plt.tight_layout()

	# fig.savefig("./plots/profile_%d_%03d.pdf"%(host,snap))
	plt.show()
