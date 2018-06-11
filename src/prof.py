#!/usr/bin/env python
import logging
import sys

import defopt
import numpy as np
import pandas as pd
from hbtp import HBTReader
from src import read


class HBTProfileReader(HBTReader):
    """Extends HBTReader with profile-reading options.
    """

    def __init__(self, subhalo_path):
        HBTReader.__init__(self, subhalo_path)

    def GetHostProfile(self, selection=None, isnap=-1):
        """Returns normalised, binned particle positions of a FoF group.
        """

        logging.info("Retrieving profile for halos %s" % str(selection))
        profile = self.LoadHostHalos(isnap, selection)["Profile"]
        return profile

    def CalculateProfile(self, TrackId, isnap=-1, bins=None):
        """Returns normalised particle positions of a subhalo.

        If bins are provided, particle positions are binned, and a density
        profile is returned.  Otherwise, raw positions, centered around
        ``ComovingAveragePosition`` and normalised to ``BoundR200CritComoving``
        are returned.
        """

        result = []
        subhalo = self.GetSub(TrackId, isnap)
        positions = (
            self.GetParticleProperties(TrackId, isnap)["ComovingPosition"]
            - subhalo["ComovingAveragePosition"][0]
        ) / subhalo["BoundR200CritComoving"]

        if bins is not None:
            distances = np.apply_along_axis(
                lambda x: np.sqrt(np.sum(np.power(x, 2.0))), 1, positions
            )
            result = np.histogram(distances, bins=bins)
        else:
            result = positions

        return result

    def CalculateHostProfile(self, HostHaloId, isnap=-1, bins=None):
        """Returns normalised particle positions of a FoF group.

        If bins are provided, particle positions are binned, and a density
        profile is returned.  Otherwise, raw positions, centered around
        ``ComovingPosition`` and normalised to ``R200CritComoving`` are
        returned.
        """

        logging.debug("Calculating profile for halo %d" % HostHaloId)
        result = []

        try:
            subhalos = self.GetSubsOfHost(HostHaloId, isnap)["TrackId"]
            hosthalo = self.LoadHostHalos(isnap, selection=HostHaloId)

            logging.debug("Found %d subhalos" % len(subhalos))

            positions = [
                (
                    (particle - hosthalo["CenterComoving"])
                    / hosthalo["R200CritComoving"]
                )[0]
                for subhalo in subhalos
                for particle in self.GetParticleProperties(subhalo, isnap)[
                    "ComovingPosition"
                ]
            ]

            logging.debug("Found %d particles" % len(positions))

            if bins is not None:
                distances = np.apply_along_axis(
                    lambda x: np.sqrt(np.sum(np.power(x, 2.0))), 1, positions
                )
                result = np.histogram(distances, bins=bins)
            else:
                result = positions

        except TypeError:
            result = []

        return result


def main(grav, snap, verbose=True):
    """Read & save halo profiles.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    :param bool verbose: print IDs to stdout?
    """
    ids = read.ids(grav, snap)
    reader = HBTProfileReader("./data/%s/subcat" % grav)
    logging.info("%d haloes at snapshot %d" % (len(ids), snap))

    profs = pd.DataFrame(
        reader.GetHostProfile([ids], snap), columns=range(0, 20), index=ids
    )

    if verbose:
        profs.to_csv(sys.stdout, sep=",", index_label="HaloId")

    return profs


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
