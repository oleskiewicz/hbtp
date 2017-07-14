IDS:=$(shell more ./output/ids.txt)

plots: $(foreach ID,$(IDS),./plots/mah_$(ID).pdf)
ids: ./output/ids.txt
docs:
	cd docs; make html

./output/ids.txt: ./src/query.py
	python $< $@

./plots/mah_%.pdf: ./output/mah_%.dot
	dot -Tpdf -o $@ $<

./output/mah_%.dot: ./src/traverse.py
	python $< $*

clean:
	rm -f ./output/*.dot

.PHONY: plots clean docs
.PRECIOUS: ./output/mah_%.dot ./output/mah_%.tsv

