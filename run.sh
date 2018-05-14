#!/usr/bin/env bash
#BSUB -P durham
#BSUB -q cosma
#BSUB -n 8
#BSUB -J hbtp_cmh
#BSUB -oo ./log/log_%J.txt
#BSUB -eo ./log/err_%J.txt

export GRAV=GR_b64n512
export SNAP=051
export NFW_f=010
export PROF=nfw

make -j8 cmh
