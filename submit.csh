#!/usr/bin/env tcsh

set file_in  = "./output/ids.txt"
set file_out = "./output/mah_liminality.tsv"

echo "nodeIndex\tsnapshotNumber\tparticleNumber" > $file_out

foreach id (`more $file_in`)
  bsub -P durham \
       -n 1 \
       -q bench1 \
       -J "mah_$id" \
       -oo ./log/log.txt \
       -eo ./log/err.txt \
       python ./src/tree.py $id $file_out
end

