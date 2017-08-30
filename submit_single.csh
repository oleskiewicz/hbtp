#!/bin/tcsh

#BSUB -P durham
#BSUB -q cordelia
#BSUB -n 1
#BSUB -J cmh_78_549
#BSUB -oo ./log/log-%I.txt
#BSUB -eo ./log/err-%I.txt

python ./src/dhalo/tree.py ./output/lim.npy 78000000000549 ./output/cmh_78.csv
