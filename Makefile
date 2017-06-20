plot: ./plots/mah.pdf

./plots/%.pdf: ./output/%.dot
	dot -Tpdf -o $@ $<

./output/mah.dot: ./src/tree.py
	$< > $@

