#!/usr/bin/env tcsh

#BSUB -q bench1
#BSUB -P durham
#BSUB -n 1
#BSUB -J dhalo_mah
#BSUB -oo log/log_1.txt
#BSUB -eo log/err_1.txt

make
