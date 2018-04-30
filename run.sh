#!/usr/bin/env bash
#BSUB -P durham
#BSUB -q cordelia
#BSUB -n 1
#BSUB -J hbtp[%I]%50
#BSUB -oo ./log/log_%J.txt
#BSUB -eo ./log/err_%J.txt

ulimit -s unlimited
ulimit -c 0

SNAP=122

# HBT+ -- ids
python -m src.hbtp.query $SNAP

# HBT+ -- CMHs
for ID `more "./output/ids-${SNAP}.txt"`; do
	python -m src.hbtp.cmh ${SNAP} ${ID}
done

# HBT+ -- combine CMHs
make -f ./src/hbtp/makefile ./output/hbtp/cmh_${SNAP}.csv

