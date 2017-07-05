#!/usr/bin/env tcsh

#BSUB -q bench1
#BSUB -P durham
#BSUB -n 1
#BSUB -J dhalo_mergertree
#BSUB -oo log/log_1.txt
#BSUB -eo log/err_1.txt

make

# python ./src/plot.py $ID ./output/mah_$ID.dot
# dot -Tpdf -o ./plots/mah_$ID.pdf ./output/mah_$ID.dot

