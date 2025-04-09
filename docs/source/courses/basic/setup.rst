.. _`basic/setup`:

IMAS validator 101: setup
========================

For these training excercises you will need an installation of imas_validator and access to IMAS-Python.
Have a look at the :ref:`installing` page for more details on installing IMAS validator.
To check if your installation worked, try

.. code-block:: console

    $ python -c 'import imas_validator; print(imas_validator.__version__)'
    0.3.0

Some IMAS-Python DBEntry objects and custom validation rulesets were built specifically for this training course.
You can build them by running

.. code-block:: console

    $ python -m imas_validator.training.training_setup

These are then generated into a ``imas-validator-course`` and a ``imas-validator-training-rulesets`` folder in your current working directory.
