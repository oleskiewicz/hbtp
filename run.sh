#!/usr/bin/env bash
#BSUB -P durham
#BSUB -q cosma
#BSUB -n 8
#BSUB -J hbtp_cmh
#BSUB -oo ./log/log_%J.txt
#BSUB -eo ./log/err_%J.txt

make cmh
