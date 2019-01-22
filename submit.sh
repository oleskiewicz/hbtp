#!/bin/sh -e

for NFW_f in 001 002 010; do
	for G in GR_b64n512 fr6_b64n512; do
		for S in 122 093 078 061 051; do
			NFW_f=${NFW_f} GRAV=${G} SNAP=${S} sbatch ./run.sh
		done;
	done;
done;
