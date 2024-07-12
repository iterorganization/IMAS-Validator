.. _`tips and tricks`:

Tips and Tricks
===============

1. To save typing and make your tests more readable, loop over array elements rather
   than indices. For example:

  .. code-block:: python

    # DON'T
    for i in range(len(ids.profiles_1d)):
      assert ids.profiles_1d[i].ion.has_value
      for j in range(len(ids.profiles_1d[i].ion)):
        assert ids.profiles_1d[i].ion[j].element.has_value
        for k in range(len(ids.profiles_1d[i].ion[j].element)):
          assert ids_profiles_1d[i].ion[j].element[k].a.has_value
    # DO
    for profiles_1d in ids.profiles_1d:
      assert profiles_1d.ion.has_value
      for ion in profiles_1d.ion:
        assert ion.element.has_value
        for element in ion.element:
          assert element.a.has_value

2. You can immediately check that all values of a ``numpy`` array adhere to a condition
   at once without building a loop. This is more efficient because numpy can use 
   optimized C code in the background.

  .. code-block:: python

    # DON'T
    for x in ids.global_quantities.ip:
      assert -1.7e7 < x <= 0
    # DO
    assert -1.7e7 < ids.global_quantities.ip <= 0
