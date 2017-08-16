#!/usr/bin/env python
import sys
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

from HBTReader import HBTReader

hostId, snap = int(sys.argv[1]), int(sys.argv[2])
reader = HBTReader("./data/")
hosthalo = reader.LoadHostHalos(snap, selection=hostId)

fig = plt.figure(1)
ax = Axes3D(fig)
fig.suptitle("FoF group %d at snapshot %d"%(hostId, snap))

ax.set_xlim3d([-5,5])
ax.set_ylim3d([-5,5])
ax.set_zlim3d([-5,5])

ax.view_init(30, 2*snap)

for trackId in reader.GetSubsOfHost(hostId, snap)['TrackId']:
	positions = (reader.GetParticleProperties(trackId, snap)['ComovingPosition']\
		- hosthalo['CenterComoving']) / hosthalo['R200CritComoving']
	ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2])

fig.savefig("./plots/profile_%d/%03d.png"%(hostId,snap))
# plt.show()
