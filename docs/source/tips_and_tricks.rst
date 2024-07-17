.. _`tips and tricks`:

Tips and Tricks
===============

1. To save typing and make your tests more readable, loop over array elements rather
   than indices when possible. For example:

  .. code-block:: python

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

    assert -1.7e7 < ids.global_quantities.ip <= 0
