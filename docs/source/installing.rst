.. _`installing`:

Installing the IMAS IDS validator
=================================

SDCC setup
----------

.. note::
  A module will become available on SDCC after the first release of IDS validator.
  Use the following instructions to work with the latest development version.

.. 
  Update SDCC setup on first release

* Setup a project folder and clone git repository

  .. code-block:: bash

    mkdir projects
    cd projects
    git clone ssh://git@git.iter.org/imex/ids-validator.git
    cd ids-validator

* Setup a python virtual environment and install python dependencies

  .. code-block:: bash

    python3 -m venv ./venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade wheel setuptools
    pip install .
    # For development an installation in editable mode may be more convenient
    # pip install -e .[all]

* Load IMAS and IMASPy.

  .. code-block:: bash

    module load IMAS IMASPy

* Test the installation

  .. code-block:: bash

    python3 -c "import ids_validator; print(ids_validator.__version__)"
    pytest


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
    cd ids-validator

* Setup a python virtual environment and install python dependencies

  .. code-block:: bash

    python3 -m venv ./venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade wheel setuptools
    pip install .
    # For development an installation in editable mode may be more convenient
    # pip install .[all]

* Install IMASPy.

  Follow the instructions from `IMASPy installation docs <https://git.iter.org/projects/IMAS/repos/imaspy/browse/docs/source/installing.rst>`_

* Test the installation

  .. code-block:: bash

    python3 -c "import ids_validator; print(ids_validator.__version__)"
    pytest

* To build the ids-validator documentation, execute:

  .. code-block:: bash

    make -C docs html
