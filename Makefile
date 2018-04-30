GRAVS:=GR_b64n512 fr6_b64n512
SNAPS:=122 093 078 061 051
PROFS:=nfw einasto

GRAV?=GR_b64n512
SNAP?=051
PROF?=nfw

SRC:=./src
OUT:=./output
IDS:=$(shell tail $(OUT)/ids.$(GRAV).$(SNAP).csv | paste -s -d' ')

ids: $(OUT)/ids.$(GRAV).$(SNAP).csv
cmh: ids $(OUT)/cmh.$(GRAV).$(SNAP).csv

$(OUT)/result.$(GRAV).$(PROF).csv: $(SRC)/process.py
	$< $(GRAV) $(PROF)

$(OUT)/cmh.$(GRAV).$(SNAP).csv: $(SRC)/forge.py $(foreach ID,$(IDS),$(OUT)/cmh.$(GRAV).$(SNAP).$(ID).csv)
	echo "HaloId,Snapshot,M200Crit" > $@
	cat $(OUT)/cmh.$(GRAV).$(SNAP).*.csv >> $@
	$< $(GRAV) $(SNAP)

$(OUT)/cmh.%.csv: $(SRC)/cmh.py
	$< $(shell echo $* | tr '.' ' ') > $@

$(OUT)/ids.$(GRAV).$(SNAP).csv: $(SRC)/filter.py
	$< $(GRAV) $(SNAP) > $@

$(OUT)/mt.%.dot: $(SRC)/mt.py
	$< $(shell echo $* | tr '.' ' ') > $@

./plots/mt.%.pdf: $(OUT)/mt.%.dot
	dot -Tpdf -o $@ $<

docs:
	cd docs; make

clean:
	cd docs; make clean
	rm -i $(OUT)/*.csv

.PHONY: purge clean docs plots cmhs ids
