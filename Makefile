# ID:=30048400000117
ID:=48048400000000

plot: ./plots/mah_$(ID).pdf

docs:
	cd docs; make html

./plots/mah_%.pdf: ./output/mah_%.dot
	dot -Tpdf -o $@ $<

./output/mah_%.dot: ./src/plot.py
	$< $* $@

.PHONY: plot docs
.PRECIOUS: ./output/*dot
