#!/usr/bin/env tcsh

#BSUB -q bench1
#BSUB -P durham
#BSUB -n 1
#BSUB -J dhalo_mergertree
#BSUB -oo log/log_1.txt
#BSUB -eo log/err_1.txt

# make

python ./src/traverse.py 48048400000000 > ./output/mah_48048400000000.dot
