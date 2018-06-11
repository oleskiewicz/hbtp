HBTplus Python toolbox
======================

Python module with helpers for analysis of dark matter haloes from HBTplus halo
finder.

Usage
-----

`Makefile` is used to document computation of targets for any given values of
gravity, snapshot, f or density profile parameters.  `run.sh` and `run_all.sh`
demonstrate sample calculation, and submission to a batch queue.

Readers
-------

- `HBTReader`: general utility class, from
  [HBTplus](github.com/Kambrian/HBTplus)
- `HBTHistoryReader`: provides an efficient collapsed mass history (CMH) calculation
- `HBTProfileReader`: provides halo and subhalo density profile reader &
  calculation; does **not** perform fitting - this is done in
  `src.process.prof()`
- `HBTEnvironmentReader`: calculates environmental proxies, as described in
  Shi+2017 (only $D_{N,f}$ so far)
