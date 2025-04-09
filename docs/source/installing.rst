.. _`installing`:

Installing the IMAS validator
=============================

SDCC module load
----------------

.. code-block:: bash

  module load imas-validator

SDCC installation
-----------------

* Setup a project folder and clone git repository

  .. code-block:: bash

    mkdir projects
    cd projects
    git clone ssh://git@git.iter.org/imex/ids-validator.git
    cd imas-validator

* Setup a python virtual environment and install python dependencies

  .. code-block:: bash

    # load IMAS and IMAS-Python before install
    module load IMAS-Python # or IMASPy
    python3 -m venv ./venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade wheel setuptools
    # For development an installation in editable mode may be more convenient
    pip install -e .[all]

* Run each session if tool already installed

  .. code-block:: bash

    # Load modules every time you use imas_validator
    module load IMAS-Python # or IMASPy
    # And activate the Python virtual environment every time you use imas_validator
    . venv/bin/activate

* Test the installation

  .. code-block:: bash

    python -c "import imas_validator; print(imas_validator.__version__)"
    python -m pytest


Ubuntu installation
-------------------

* Install system packages

  .. code-block:: bash

    sudo apt update
    sudo apt install build-essential git-all python3-dev python-is-python3 \
      python3 python3-venv python3-pip python3-setuptools

* Setup a project folder and clone git repository

  .. code-block:: bash

    mkdir projects
    cd projects
    git clone ssh://git@git.iter.org/imex/ids-validator.git
    cd imas-validator

* Setup a python virtual environment and install python dependencies

  .. code-block:: bash

    python3 -m venv ./venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade wheel setuptools
    # For development an installation in editable mode may be more convenient
    pip install .[all]

* Install IMAS-Python.

  Follow the instructions from `IMAS-Python installation docs <https://imas-python.readthedocs.io/en/latest/installing.html>`_

* Test the installation

  .. code-block:: bash

    python -c "import imas_validator; print(imas_validator.__version__)"
    python -m pytest

* To build the IMAS-Validator documentation, execute:

  .. code-block:: bash

    make -C docs html
