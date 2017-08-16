#!/usr/bin/env python
import sys
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

from HBTReader import HBTReader

hostId, snap = int(sys.argv[1]), int(sys.argv[2])
reader=HBTReader("./data/")
# subhalo = reader.GetSub(trackId, snap)

fig = plt.figure(1)
ax = Axes3D(fig)
fig.suptitle("FoF group %d at snapshot %d"%(hostId, snap))

# ax.set_xlim3d([-2,2])
# ax.set_ylim3d([-2,2])
# ax.set_zlim3d([-2,2])

ax.view_init(30, 2*snap)

for trackId in reader.GetSubsOfHost(hostId, snap)['TrackId']:
	positions = reader.GetParticleProperties(trackId, snap)['ComovingPosition']
	ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2])
	# ax.plot([0.0], [0.0], [0.0], 'ro')

	# u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
	# ax.plot_wireframe(np.cos(u)*np.sin(v), np.sin(u)*np.sin(v), np.cos(v), color="r")

fig.savefig("./plots/profile_%d/%03d.png"%(hostId,snap))
# plt.show()
