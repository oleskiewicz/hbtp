ID:=30048400000117

plot: ./plots/mah_$(ID).pdf

./plots/mah_%.pdf: ./output/mah_%.dot
	dot -Tpdf -o $@ $<

./output/mah_%.dot: ./src/plot.py
	$< $* $@

.PRECIOUS: ./output/*dot
