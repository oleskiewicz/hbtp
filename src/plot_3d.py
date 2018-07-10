#!/usr/bin/env python3
import logging

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

import util
from hbtp import HBTReader


def main(grav, snap, host, save=False):
    """Plot 3D particles belonging to host halo

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param int host: Host halo ID
    :param bool save: save figure to file?
    """
    reader = HBTReader("./data/%s/subcat" % grav)

    for snap in range(11, 79):

        loggging.debug("FoF group %d at snapshot %d" % (host, snap))

        # for angle in range(100,360):
        fig = plt.figure()
        # fig.suptitle("FoF group %d at snapshot %d"%(host, snap))

        # # left panel - 3D partile positions
        # ax = fig.add_subplot(1, 1, 1, projection='3d')

        # ax.set_xlim3d([-5,5])
        # ax.set_ylim3d([-5,5])
        # ax.set_zlim3d([-5,5])

        # ax.view_init(30, angle)#(2*snap))

        # for trackId in reader.GetSubsOfHost(host, snap)['TrackId']:
        #   positions = (reader.GetParticleProperties(trackId, snap)['ComovingPosition']\
        #     - hosthalo['CenterComoving']) / hosthalo['R200CritComoving']
        #   ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],\
        #     marker='.')

        # right panel - density profile
        ax = fig.add_subplot(1, 1, 1)

        p = np.array(reader.GetHostProfile(host, snap)[0], dtype=np.float)
        p = np.cumsum(p)
        p = np.divide(p, p[-1])
        x = np.linspace(-2.0, 0.0, 20)

        ax.set_xlabel(r"$\log_{10}(r/r_{200})$")
        ax.set_ylabel(r"$\log_{10}(M(<r)/M_{200})$")
        ax.set_xlim([-2.1, 0.1])
        ax.set_ylim([-2.1, 0.1])

        # prof = np.array(prof, dtype=np.float32)
        # prof = np.cumsum(prof)
        # prof = np.log10(np.divide(prof, prof[-1]))
        # # prof = util.normalise(prof)

        ax.plot(x, np.log10(p))

        # plt.tight_layout()

        if save:
            fig.savefig("./plots/profile.%s.%03d_%d.png" % (grav, snap, host))
        else:
            plt.show()


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
