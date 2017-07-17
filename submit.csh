#!/usr/bin/env tcsh

echo "nodeIndex\tsnapshotNumber\tparticleNumber" > ./output/mah.tsv
foreach id (`more ./output/ids.txt`)
  bsub -P durham \
       -n 1 \
       -q bench1 \
       -J "mah_$id" \
       -oo ./log/log.txt \
       -eo ./log/err.txt \
       python ./src/tree.py $id
end

