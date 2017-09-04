#!/usr/bin/env tcsh

set snap = 051

# ################################################################################
# # DHalo -- CMH                                                                 #
# ################################################################################
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

# ################################################################################
# # HBT+ -- ids                                                                  #
# ################################################################################
# bsub -P durham \
#      -n 1 \
#      -q cordelia \
#      -J "ids_$snap" \
#      -oo ./log/log_%J.txt \
#      -eo ./log/err_%J.txt \
#      python -m src.hbtp.query $snap

# ################################################################################
# # HBT+ -- properties                                                           #
# ################################################################################
# bsub -P durham \
#      -n 1 \
#      -q cordelia \
#      -J "props_$snap" \
#      -oo ./log/log_%J.txt \
#      -eo ./log/err_%J.txt \
#      python -m src.hbtp.prop ${snap}

# ################################################################################
# # HBT+ -- density profiles                                                     #
# ################################################################################
# bsub -P durham \
#      -n 1 \
#      -q cordelia \
#      -J "profs_$snap" \
#      -oo ./log/log_%J.txt \
#      -eo ./log/err_%J.txt \
#      python -m src.hbtp.prof ${snap}

################################################################################
# HBT+ -- merger trees                                                         #
################################################################################
foreach id (`more "./output/hbtp/ids.txt"`)
	bsub -P durham \
			 -n 1 \
			 -q cordelia \
			 -J "cmh_${snap}_${id}" \
			 -oo ./log/log_%J.txt \
			 -eo ./log/err_%J.txt \
			 python -m src.hbtp.cmh ${snap} ${id}
end
