Merger Tree visualisation
=========================

	.
	├── data -> /gpfs/data/Galform/Merger_Trees/Millennium/new/treedir_063
	├── log
	├── Makefile
	├── output
	├── plots
	├── README.md
	└── src
	    ├── __init__.py
	    ├── plot.py
	    ├── query.py
	    ├── read.py
	    └── read.pyc

## DHalo

### Tree traversal method

**recursive**
: every time a node is reached, it searches for all nodes for
	which this node is a descendant (*progenitors*);	it then runs itself starting
	from this node; this ensures that merger trees generated at any given node
	are identical below that node

**pure**
: the function output only depends on the inputs;  no global
	variables are used;  function calls itself recursively with all necessary
	variables updated for the run

**skipping "double progenitor" histories**
: it can happen, if subhaloes "swap" between host haloes, that one halo
	belongs two separate trees (see halo `36048400001731`, which belongs both to
	`37048400000752` and `37048400001615` histories)

**de-duplicating**
: implemented by only recursing if progenitors' id is not in the list of
	already visited nodes, prevents multiple traversals;	as of now, it also
	causes *skipping "double progenitor" histories*, and should be investigated
	further

### Tree diagram

- deduplicate:
	1. select all nodes
	1. for each halo select all pregenitors
	1. select hosts of all progenitors
	1. keep unique hosts
	1. check if `mah` has been ran for this node
	1. run recursively for each progenitor
- hosts_only:
	1. select only nodes which are top-level (host) haloes
	1. for each halo select all pregenitors
	1. run recursively for each progenitor
- include_subhaloes:
	1. select all nodes
	1. for each halo select all pregenitors
	1. run recursively for each progenitor

## TODO

- [ ] fix build system
	- `cosma` worker nodes do not have `graphviz` module loaded by default, unlike
		the login nodes
- [ ] implement tree traversal into Galform merger tree format

