#!/usr/bin/env bash
#BSUB -P durham
#BSUB -q bench1
#BSUB -n 1
#BSUB -J hbtp
#BSUB -oo ./log/log_%J.txt
#BSUB -eo ./log/err_%J.txt

export GRAV=GR_b64n512
export SNAP=051
make -n -j4 ./output/cmh.${GRAV}.${SNAP}.csv
