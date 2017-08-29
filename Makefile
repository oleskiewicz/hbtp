docs:
	cd docs; make html

purge:
	rm -f ./output/*

.PHONY: docs purge

