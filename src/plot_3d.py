#!/usr/bin/env python
import sys
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

from HBTReader import HBTReader

hostId, snap = int(sys.argv[1]), int(sys.argv[2])
reader = HBTReader("./data/")
hosthalo = reader.LoadHostHalos(snap, selection=hostId)

fig = plt.figure(figsize=plt.figaspect(2.0))
fig.suptitle("FoF group %d at snapshot %d"%(hostId, snap))

# left panel - 3D partile positions
ax = fig.add_subplot(2, 1, 1, projection='3d')

ax.set_xlim3d([-5,5])
ax.set_ylim3d([-5,5])
ax.set_zlim3d([-5,5])

ax.view_init(30, 2*snap)

for trackId in reader.GetSubsOfHost(hostId, snap)['TrackId']:
	positions = (reader.GetParticleProperties(trackId, snap)['ComovingPosition']\
		- hosthalo['CenterComoving']) / hosthalo['R200CritComoving']
	ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2])

# right panel - density profile
ax = fig.add_subplot(2, 1, 2)

ax.set_xlabel("r")
ax.set_ylabel("differential mass")
ax.set_xlim([-2.75, 0.25])
ax.set_ylim([-3.0, 0.0])

prof, edges = reader.GetHostProfile(hostId, snap, bins=np.logspace(-2.5, 0.0, 32))
midpoints = 0.5*(np.log10(edges)[1:] + np.log10(edges)[:-1])
prof = prof/float(prof[-1])

ax.plot(midpoints, np.log10(prof))

plt.tight_layout()
fig.savefig("./plots/profile_%d/%03d.png"%(hostId,snap))
# plt.show()
