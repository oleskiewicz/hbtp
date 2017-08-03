#!/usr/bin/env python
import sys
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

from HBTReader import HBTReader

trackId, snap = int(sys.argv[1]), int(sys.argv[2])
reader=HBTReader("./data/")
particles = reader.GetProfile(trackId, snap)

fig = plt.figure(1)
ax = Axes3D(fig)
fig.suptitle("subhalo %d at snapshot %d"%(trackId, snap))

ax.set_xlim3d([-2,2])
ax.set_ylim3d([-2,2])
ax.set_zlim3d([-2,2])

ax.view_init(30, snap)
ax.plot(particles[:, 0], particles[:, 1], particles[:, 2], 'b.')
ax.plot([0.0], [0.0], [0.0], 'ro')

u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
ax.plot_wireframe(np.cos(u)*np.sin(v), np.sin(u)*np.sin(v), np.cos(v), color="r")

fig.savefig("./plots/profile_%d/%03d.png"%(trackId,snap))
# plt.show()