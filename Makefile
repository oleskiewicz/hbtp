# IDS:=$(shell more ./output/ids.txt)
IDS:=37048400001615

plots: $(foreach ID,$(IDS),./plots/mah_$(ID).pdf)
mah: ./plots/mah.pdf
ids: ./output/ids.txt
docs:
	cd docs; make html

./output/ids.txt: ./src/query.py
	python $< $@

./plots/mah_%.pdf: ./output/mah_%.dot
	dot -Tpdf -o $@ $<

./output/mah_%.dot: ./src/traverse.py
	python $< $*

./plots/mah.pdf: ./src/plot.py ./output/mah.tsv
	python $< $(word 2,$^) $@

# only re-run after re-running submit.csh on new set if ids
./output/mah.tsv: ./src/forge.py
	python $< $@

clean:
	rm -f ./output/*.dot

purge:
	rm -f ./output/*

.PHONY: plots mah purge clean docs
.PRECIOUS: ./output/mah_%.dot ./output/mah_%.tsv

