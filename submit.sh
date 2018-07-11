#!/bin/sh

for G in GR_b64n512 fr6_b64n512; do
	for S in 122 093 078 061 051; do
		GRAV=${G} SNAP=${S} bsub < ./run.sh
	done;
done;
