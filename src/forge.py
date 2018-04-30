#!/usr/bin/env python
import defopt
import pandas as pd


def forge(data):
    """Un-melts (forges) the DataFrame from long format to a wide one

    In essence, we want to go from

    ======= ========= =========
    HaloId  Snapshot  M200Crit
    ======= ========= =========
    1       11        0
    1       12        0
    1       13        0
    1       14        324
    1       15        653
    1       16        849
    1       17        1204
    1       ...       ...
    2       10        0
    2       11        0
    2       12        0
    2       13        0
    2       14        0
    2       15        132
    2       16        661
    2       17        945
    2       ...       ...
    ...
    ======= ========= =========

    to

    ======= ==== ==== ==== ==== ==== ==== ==== ==== ====
    HaloId  10   11   12   13   14   15   16   17   ...
    ======= ==== ==== ==== ==== ==== ==== ==== ==== ====
    1       NA   0    0    0    324  653  849  1204 ...
    2       0    0    0    0    0    132  661  945  ...
    ...
    ======= ==== ==== ==== ==== ==== ==== ==== ==== ====

    as described in https://cran.r-project.org/web/packages/reshape2/reshape2.pdf

    Note:
        Because IDs in HBT+ change, each row in *wide* format corresponds to a halo
        of ``HaloId``, as identified at snapshot ``IdentificationSnapshot``
    Arguments:
        data (pandas.DataFrame): input CMH DataFrame in a long format, read from a
            TSV written by :mod:`src.hbtp.cmh`
    Returns:
        pandas.DataFrame: output CMH DataFrame in a wide format
    """
    return data.pivot_table(\
     values='M200Crit',\
     columns='Snapshot',
     index='HaloId')


def main(grav, snap):
    """Query & filter halo IDs.

    :param str grav: Gravity (GR_b64n512 or fr6_b64n512)
    :param int snap: Snapshot number (between 122 and 10)
    """
    f = "./output/cmh.%s.%03d.csv" % (grav, snap)
    long = pd.read_csv(f, sep=",")
    wide = forge(long)
    wide.to_csv(f, sep=",")


if __name__ == '__main__':
    defopt.run(main, strict_kwonly=False)
