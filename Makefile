SRC:=./src
OUT:=./output

ids: $(OUT)/ids.$(GRAV).$(SNAP).csv
cmh: ids $(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv

$(OUT)/ids.$(GRAV).$(SNAP).csv: $(SRC)/filter.py
	$< $(GRAV) $(SNAP) > $@

$(OUT)/result.$(PROF).csv: $(SRC)/process.py
	$< $(PROF)

$(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv: $(SRC)/cmh.py $(OUT)/ids.$(GRAV).$(SNAP).csv
	$(SRC)/cmh.py \
		$(GRAV) $(SNAP) \
		-H $(shell cat $(OUT)/ids.$(GRAV).$(SNAP).csv | paste -s -d' ') \
		-f $(shell echo "$(NFW_f) / 100" | bc -l) \
		> $@

$(OUT)/mt.%.dot: $(SRC)/mt.py
	$< $(shell echo $* | tr '.' ' ') > $@

./plots/mt.%.pdf: $(OUT)/mt.%.dot
	dot -Tpdf -o $@ $<

docs:
	cd docs; make

clean:
	cd docs; make clean
	rm -i $(OUT)/*.txt

.PHONY: purge clean docs plots cmhs ids
