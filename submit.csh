#!/usr/bin/env tcsh

set SNAP = 122

# ################################################################################
# # HBT+ -- ids                                                                  #
# ################################################################################
# bsub \
# 	-P durham -n 1 -q cordelia \
# 	-oo ./log/log_%J.txt -eo ./log/err_%J.txt \
# 	-J "ids_$SNAP" \
# 	python -m src.hbtp.query $SNAP

################################################################################
# HBT+ -- CMHs                                                                 #
################################################################################
bsub \
	-P durham -n 1 -q cordelia \
	-J "cmh_${SNAP}_0" \
	-We 6:00 \
	-oo "./log/log_%J.0.txt" -eo "./log/err_%J.0.txt" \
	python -m src.hbtp.cmh ${SNAP} 0
foreach id (`tail -n +2 "./output/ids-${SNAP}.txt"`)
	bsub \
		-P durham -n 1 -q cordelia \
		-J "cmh_${SNAP}[${id}]%50" \
		-We 3:00 \
		-oo ./log/log_%J.%I.txt -eo ./log/err_%J.%I.txt \
		python -m src.hbtp.cmh ${SNAP} ${id}
end

# ################################################################################
# # HBT+ -- combine CMHs                                                         #
# ################################################################################
# bsub\
# 	-P durham -n 1 -q cordelia \
# 	-oo ./log/log_%J.txt -eo ./log/err_%J.txt \
# 	-J "cmhcomb_$SNAP" \
# 	make -f ./src/hbtp/makefile ./output/hbtp/cmh_${SNAP}.csv
