GRAVS:=GR_b64n512 fr6_b64n512
SNAPS:=122 093 078 061 051
PROFS:=nfw einasto

SRC:=./src
OUT:=./output
IDS:=$(shell cat $(OUT)/ids.$(GRAV).$(SNAP).csv | paste -s -d' ')

ids: $(OUT)/ids.$(GRAV).$(SNAP).csv
cmh: ids $(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv

$(OUT)/ids.$(GRAV).$(SNAP).csv: $(SRC)/filter.py
	$< $(GRAV) $(SNAP)

$(OUT)/result.$(PROF).csv: $(SRC)/process.py
	$< $(PROF)

$(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).csv: $(SRC)/forge.py $(foreach ID,$(IDS),$(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).$(ID).txt)
	echo "HaloId,Snapshot,M200Crit" > $@
	cat $(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).*.txt >> $@
	$< $@

$(OUT)/cmh.f$(NFW_f).$(GRAV).$(SNAP).%.txt: $(SRC)/cmh.py
	$< $(GRAV) $(SNAP) $* -f $(shell echo "$(NFW_f) / 100" | bc -l)

$(OUT)/mt.%.dot: $(SRC)/mt.py
	$< $(shell echo $* | tr '.' ' ') > $@

./plots/mt.%.pdf: $(OUT)/mt.%.dot
	dot -Tpdf -o $@ $<

docs:
	cd docs; make

clean:
	cd docs; make clean
	rm -i $(OUT)/.*.csv

.PHONY: purge clean docs plots cmhs ids
