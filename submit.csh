#!/usr/bin/env tcsh

set snap = 122

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
# bsub \
# 	-P durham -n 1 -q cordelia \
# 	-oo ./log/log_%J.txt -eo ./log/err_%J.txt \
# 	-J "ids_$snap" \
# 	python -m src.hbtp.query $snap

# ################################################################################
# # HBT+ -- properties                                                           #
# ################################################################################
# bsub \
# 	-P durham -n 1 -q cordelia \
# 	-oo ./log/log_%J.txt -eo ./log/err_%J.txt \
# 	-J "props_$snap" \
# 	python -m src.hbtp.prop ${snap}
# ################################################################################
# # HBT+ -- density profiles                                                     #
# ################################################################################
# bsub \
# 	-P durham -n 1 -q cordelia \
# 	-oo ./log/log_%J.txt -eo ./log/err_%J.txt \
# 	-J "profs_$snap" \
# 	python -m src.hbtp.prof ${snap}

# ################################################################################
# # HBT+ -- CMHs                                                                 #
# ################################################################################
# foreach id (`head -n 1000 "./output/hbtp/ids_${snap}.txt"`)
# 	bsub\
# 		-P durham -n 1 -q cordelia \
# 		-J "cmh_${snap}[${id}]%40" \
# 		-oo ./log/log_%J.%I.txt -eo ./log/err_%J.%I.txt \
# 		python -m src.hbtp.cmh ${snap} ${id}
# end

# ################################################################################
# # HBT+ -- combine CMHs                                                         #
# ################################################################################
# bsub\
# 	-P durham -n 1 -q cordelia \
# 	-oo ./log/log_%J.txt -eo ./log/err_%J.txt \
# 	-J "cmhcomb_$snap" \
# 	make -f ./src/hbtp/makefile ./output/hbtp/cmh_${snap}.csv
