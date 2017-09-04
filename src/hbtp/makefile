SRC:=./src/hbtp
OUT:=./output/hbtp
SNAP:=051
# IDS:=$(shell more $(OUT)/ids_$(SNAP).txt)
IDS:=0 1 2 3 4 5 6 7 8 9

ids: $(OUT)/ids_$(SNAP).txt
props: $(foreach ID,$(IDS),$(OUT)/prop_$(SNAP).csv)
profs: $(foreach ID,$(IDS),$(OUT)/prof_$(SNAP).csv)
cmhs: $(foreach ID,$(IDS),$(OUT)/cmh_$(SNAP)_$(ID).csv)
plots: $(foreach ID,$(IDS),./plots/mt_$(SNAP)_$(ID).pdf)

$(OUT)/ids_$(SNAP).txt: $(SRC)/query.py
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP)

$(OUT)/prof_$(SNAP).csv: $(SRC)/prof.py ids
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP)

$(OUT)/prop_$(SNAP).csv: $(SRC)/prop.py ids
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP)

./plots/mt_$(SNAP)_%.pdf: $(OUT)/mt_$(SNAP)_%.dot
	dot -Tpdf -o $@ $<

$(OUT)/cmh_$(SNAP)_%.csv: $(SRC)/cmh.py
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP) $* 

$(OUT)/cmh_$(SNAP).csv: $(SRC)/forge.py
	printf "HostHaloId,IdentificationSnapshot,Snapshot,M200Crit\n" > $@
	cat $(OUT)/cmh_$(SNAP)_*.csv >> $@
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP)

# ./plots/cmh_$(SNAP).pdf: $(SRC)/plot/cmh.py $(OUT)/cmh_$(SNAP).csv
# 	python $< $(word 2,$^) $@

# ./plots/dp_$(SNAP).pdf: $(SRC)/plot/dp.py $(OUT)/dp_$(SNAP).csv
# 	python $< $(word 2,$^) $@

./plots/profile.mp4: $(SRC)/plot_3d.py
	for snap in `seq 122 -1 11`; do python $< $$snap; done
	ffmpeg -pattern_type glob -i "./plots/profile*.png" $@
	rm -f "./plots/profile*.png"

clean:
	rm -f $(OUT)/*.{dot,csv}

purge:
	rm -f $(OUT)/*

.PHONY: purge clean docs plots cmhs ids
