=====================================
Merger Tree traversal's documentation
=====================================

Modules
=======

.. toctree::
	:glob:

	**

Data
====

Data files, for Millennium (Galform, DHalo format) and Liminality simulations::

  data
  ├── liminality
  │   ├── fr
  │   │   ├── dhalo
  │   │   │   ├── particle_list_122.0.hdf5
  │   │   │   └── tree_122.0.hdf5
  │   │   └── hbt -> /gpfs/data/rrtx34/fr6_b64n512/new_HBT/subcat/
  │   └── gr
  │       ├── dhalo
  │       │   ├── particle_list_122.0.hdf5
  │       │   └── tree_122.0.hdf5
  │       └── hbt -> /gpfs/data/rrtx34/GR_b64n512/new_HBT/subcat/
  └── millennium -> /gpfs/data/Galform/Merger_Trees/Millennium/new/treedir_063

Use ``ln -s`` to link ``data`` directory here to an appropriate catalogue.

Merger tree types
=================

DHalo
-----

Tree traversal method
'''''''''''''''''''''

recursive:
	every time a node is reached, it searches for all nodes for
	which this node is a descendant (*progenitors*);	it then runs itself starting
	from this node; this ensures that merger trees generated at any given node
	are identical below that node

pure:
	the function output only depends on the inputs;  no global
	variables are used;  function calls itself recursively with all necessary
	variables updated for the run

skipping "double progenitor" histories:
	it can happen, if subhaloes "swap" between host haloes, that one halo
	belongs two separate trees (see halo ``36048400001731``, which belongs both to
	``37048400000752`` and ``37048400001615`` histories)

de-duplicating *nodes*:
	implemented by only recursing if progenitors' id is not in the list of
	already visited nodes, prevents multiple traversals;	as of now, it also
	causes *skipping "double progenitor" histories*, and should be investigated
	further

de-duplicating *links*:
	like above, but replace ``element not in visited_halo_ids`` with ``link not in
	visited_halo_links``, and save the links instead of ids

only keeping main progenitors:
  function only branches off if the ``prog_host_id`` has ``isMainProgenitor ==
  1``

Tree diagram
''''''''''''

- deduplicate:
	#. select all nodes
	#. for each halo select all pregenitors
	#. select hosts of all progenitors
	#. keep unique hosts
	#. check if ``mah`` has been ran for this node
	#. run recursively for each progenitor
- hosts_only:
	#. select only nodes which are top-level (host) haloes
	#. for each halo select all pregenitors
	#. run recursively for each progenitor
- include_subhaloes:
	#. select all nodes
	#. for each halo select all pregenitors
	#. run recursively for each progenitor

Directory
=========

::

  .
  ├── data -> /gpfs/data/Galform/Merger_Trees/Millennium/new/treedir_063
  ├── docs
  ├── env
  ├── log -> /cosma/home/dp004/dc-oles1/data/galform_merger_trees/log/
  ├── logging.conf
  ├── Makefile
  ├── matplotlibrc -> ../.config/matplotlib/stylelib/minimal.mplstyle
  ├── output -> /cosma/home/dp004/dc-oles1/data/galform_merger_trees/output/
  ├── plots -> /cosma/home/dp004/dc-oles1/data/galform_merger_trees/plots/
  ├── README.rst
  ├── requirements.txt
  ├── src
  │   ├── dot.py
  │   ├── forge.py
  │   ├── halo.py
  │   ├── __init__.py
  │   ├── plot.py
  │   ├── query.py
  │   ├── read.py
  │   └── tree.py
  ├── submit.csh
  ├── submit_array.csh
  └── tags

