SRC:=./src
OUT:=./output

GRAV?=GR_b64n512
SNAP?=051
NFW_f?=002
PROF?=nfw

all: ids prof cmh dnf split

ids: $(OUT)/ids.$(GRAV).$(SNAP).csv
prof: $(OUT)/prof.$(GRAV).$(SNAP).csv
cmh: $(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv
dnf: $(OUT)/dnf.$(GRAV).$(SNAP).csv
split: $(OUT)/ids_over.$(GRAV).$(SNAP).csv $(OUT)/ids_under.$(GRAV).$(SNAP).csv

$(OUT)/ids.$(GRAV).$(SNAP).csv: $(SRC)/query.py
	python -m $(shell echo src.$$(basename $< .py)) $(GRAV) $(SNAP) > $@

$(OUT)/prof.$(GRAV).$(SNAP).csv: $(SRC)/prof.py
	python -m $(shell echo src.$$(basename $< .py)) $(GRAV) $(SNAP) > $@

$(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv: $(SRC)/cmh.py $(OUT)/ids.$(GRAV).$(SNAP).csv
	python -m $(shell echo src.$$(basename $< .py)) \
		$(GRAV) $(SNAP) \
		-H $(shell cat $(OUT)/ids.$(GRAV).$(SNAP).csv | paste -s -d' ') \
		-f $(shell echo "$(NFW_f) / 100" | bc -l) \
		> $@

$(OUT)/dnf.$(GRAV).$(SNAP).csv: $(SRC)/environment.py $(OUT)/ids.$(GRAV).$(SNAP).csv
	python -m $(shell echo src.$$(basename $< .py)) \
		$(GRAV) $(SNAP) \
		> $@

$(OUT)/ids_over.$(GRAV).$(SNAP).csv $(OUT)/ids_under.$(GRAV).$(SNAP).csv: $(SRC)/split_by_Dnf.py $(OUT)/dnf.$(GRAV).$(SNAP).csv
	python -m $(shell echo src.$$(basename $< .py)) $(GRAV) $(SNAP)

$(OUT)/result.$(PROF).csv: $(SRC)/process.py
	python -m $(shell echo src.$$(basename $< .py)) > $@

$(OUT)/mt.%.dot: $(SRC)/mt.py
	python -m $(shell echo src.$$(basename $< .py)) $(shell echo $* | tr '.' ' ') > $@

./plots/mt.%.pdf: $(OUT)/mt.%.dot
	dot -Tpdf -o $@ $<

docs:
	cd docs; make

clean:
	cd $(OUT); find -maxdepth 1 -size 0 -print | xargs wc -l

.PHONY: clean docs cmh prof ids
