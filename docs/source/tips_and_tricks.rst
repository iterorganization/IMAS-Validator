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

  If you do also need the index, you can use ``enumerate`` to get both without
  having to loop explicitly:

  .. code-block:: python

    for i, profiles_1d in enumerate(ids.profiles_1d):
      assert profiles_1d.ion.has_value
      ... # rest of code

2. You can immediately check whether all values of an array adhere to a condition
   without building a loop. This is more efficient because it uses ``numpy``
   optimized C code in the background.

  .. code-block:: python

    assert -1.7e7 < ids.global_quantities.ip <= 0
