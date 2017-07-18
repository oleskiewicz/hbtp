.. todo::

  - implement tree building methods for HBT format (now that DHalo is done)

  - plan merging this repository with existing Python utilities (from
    ``halo_data`` project)

  - redesign :func:`src.tree.build` to support this (might run out of memory in
    a heap otherwise)

    - see ``my_list_len_v2`` from
      https://www.southampton.ac.uk/~fangohr/software/ocamltutorial/lecture4.html
      for the example of tail recursion

  - implement Aaron's :math:`f` parameter (in place of NFW one)

    - requires density profile data, or at the very least :math:`c` value

