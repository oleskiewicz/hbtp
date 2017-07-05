include config.mk

plot: ./plots/mah_$(ID).pdf

docs:
	cd docs; make html

./plots/mah_%.pdf: ./output/mah_%.dot
	dot -Tpdf -o $@ $<

./output/mah_%.dot: ./src/plot.py
	python $< $* $@

clean:
	rm -f ./output/*.dot

.PHONY: plot clean docs
.PRECIOUS: ./output/mah_%.dot

