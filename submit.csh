#!/usr/bin/env tcsh

# ################
# # DHalo -- CMH #
# ################
# set file_in  = "./output/ids.txt"
# set file_out = "./output/mah_liminality.tsv"
# echo "nodeIndex\tsnapshotNumber\tparticleNumber" > $file_out
# foreach id (`more $file_in`)
#   bsub -P durham \
#        -n 1 \
#        -q bench1 \
#        -J "mah_$id" \
#        -oo ./log/log.txt \
#        -eo ./log/err.txt \
#        python ./src/tree.py $id $file_out
# end

################
# HBT+ -- prof #
################
set snap = 122
bsub -P durham \
     -n 1 \
     -q cordelia \
     -J "prof_$snap" \
     -oo ./log/log_%J.txt \
     -eo ./log/err_%J.txt \
     python ./src/HBTReader.py $snap

