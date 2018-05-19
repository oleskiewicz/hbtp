SRC:=./src
OUT:=./output

GRAV?=GR_b64n512
SNAP?=051
NFW_f?=002
PROF?=nfw

ids: $(OUT)/ids.$(GRAV).$(SNAP).csv
prof: $(OUT)/prof.$(GRAV).$(SNAP).csv
cmh: ids $(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv

$(OUT)/ids.$(GRAV).$(SNAP).csv: $(SRC)/filter.py
	$< $(GRAV) $(SNAP) > $@

$(OUT)/prof.$(GRAV).$(SNAP).csv: $(SRC)/prof.py
	$< $(GRAV) $(SNAP) > $@

$(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv: $(SRC)/cmh.py $(OUT)/ids.$(GRAV).$(SNAP).csv
	$(SRC)/cmh.py \
		$(GRAV) $(SNAP) \
		-H $(shell cat $(OUT)/ids.$(GRAV).$(SNAP).csv | paste -s -d' ') \
		-f $(shell echo "$(NFW_f) / 100" | bc -l) \
		> $@

$(OUT)/result.$(PROF).csv: $(SRC)/process.py
	$< > $@

$(OUT)/mt.%.dot: $(SRC)/mt.py
	$< $(shell echo $* | tr '.' ' ') > $@

./plots/mt.%.pdf: $(OUT)/mt.%.dot
	dot -Tpdf -o $@ $<

docs:
	cd docs; make

clean:
	cd $(OUT); find -maxdepth 1 -size 0 -print | xargs wc -l

.PHONY: clean docs cmh prof ids
