.. _`installing`:

Installing the IMAS-Validator
=============================

To get started, you can install it from `pypi.org <https://pypi.org/project/imas-validator>`_:

.. code-block:: bash

    pip install imas-validator


Local installation from sources
-------------------------------

We recommend using a :external:py:mod:`venv`. Then, clone the IMAS-Validator repository
and run `pip install`:

.. code-block:: bash

    python3 -m venv ./venv
    . venv/bin/activate
    
    git clone git@github.com:iterorganization/IMAS-Validator.git
    cd IMAS-Validator
    pip install --upgrade pip
    pip install --upgrade wheel setuptools
    pip install .[all]


* To test the installation

  .. code-block:: bash

    python -c "import imas_validator; print(imas_validator.__version__)"
    python -m pytest

* To build the IMAS-Validator documentation, execute:

  .. code-block:: bash

    make -C docs html

