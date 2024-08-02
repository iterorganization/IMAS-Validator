.. _`basic/setup`:

IDS validator 101: setup
========================

For these training excercises you will need an installation of ids_validator and access to IMASPy.
Have a look at the :ref:`installing` page for more details on installing IDS validator.
To check if your installation worked, try

.. code-block:: console

    $ python -c 'import ids_validator; print(ids_validator.__version__)'
    1.0.0

Some IMASpy DBEntry objects were built specifically for this training course that we will use.
You can build them by running

.. code-block:: console

    $ python -m ids_validator.training.create_db_entry
