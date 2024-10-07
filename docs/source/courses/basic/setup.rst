.. _`basic/setup`:

IDS validator 101: setup
========================

For these training excercises you will need an installation of ids_validator and access to IMASPy.
Have a look at the :ref:`installing` page for more details on installing IDS validator.
To check if your installation worked, try

.. code-block:: console

    $ python -c 'import ids_validator; print(ids_validator.__version__)'
    0.3.0

Some IMASpy DBEntry objects and custom validation rulesets were built specifically for this training course.
You can build them by running

.. code-block:: console

    $ python -m ids_validator.training.training_setup

These are then generated into a ``ids-validator-course`` and a ``ids-validator-training-rulesets`` folder in your current working directory.
