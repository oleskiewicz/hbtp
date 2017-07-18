#!/bin/tcsh

#BSUB -P durham
#BSUB -q cordelia
#BSUB -n 1
#BSUB -J mah_[1-20]
#BSUB -oo ./log/log_%I.txt
#BSUB -eo ./log/err_%I.txt

python ./src/tree.py $LSB_JOBINDEX
