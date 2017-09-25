SRC:=./src/hbtp
OUT:=./output/hbtp
SNAP:=051
IDS:=$(shell more $(OUT)/ids-$(SNAP).txt)

ids: $(OUT)/ids-$(SNAP).txt
props: $(foreach ID,$(IDS),$(OUT)/prop-$(SNAP).csv)
profs: $(foreach ID,$(IDS),$(OUT)/prof-$(SNAP).csv)
cmhs: $(foreach ID,$(IDS),$(OUT)/cmh-$(SNAP)_$(ID).csv) $(OUT)/cmh-$(SNAP).csv
plots: $(foreach ID,$(IDS),./plots/mt-$(SNAP)_$(ID).pdf)

$(OUT)/ids-$(SNAP).txt: $(SRC)/query.py
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP)

$(OUT)/prof-$(SNAP).csv: $(SRC)/prof.py ids
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP)

$(OUT)/prop-$(SNAP).csv: $(SRC)/prop.py ids
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP)

./plots/mt-$(SNAP)_%.pdf: $(OUT)/mt_$(SNAP)_%.dot
	dot -Tpdf -o $@ $<

$(OUT)/cmh-$(SNAP)_%.csv: $(SRC)/cmh.py
	python -m $(patsubst %.py,%,$(subst /,.,$<)) $(SNAP) $* 

$(OUT)/cmh-$(SNAP).csv: $(SRC)/forge.py
	printf "HaloId,Snapshot,M200Crit\n" > $@
	cat $(OUT)/cmh-$(SNAP)_*.csv >> $@
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
