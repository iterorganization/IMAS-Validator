.. _`ci configuration`:

CI configuration
================

IMAS-Validator uses `GitHub Actions <https://github.com/features/actions>`_ for CI. This page provides an overview
of the CI Plan and deployment processes. 


CI Plan
-------

The CI plan consists of 3 types of workflows:

* Linting 
    Runs ``black``, ``flake8``, ``mypy`` and ``isort`` on the IMAS-Validator code base.
    See :ref:`code style and linting`.
    This workflow is defined in `.github/workflows/linting.yml <https://github.com/iterorganization/IMAS-Validator/blob/develop/.github/workflows/linting.yml>`_.

* Testing
    This runs all unit tests with pytest, for various versions of Python.
    This workflow is defined in `.github/workflows/test_with_pytest.yml <https://github.com/iterorganization/IMAS-Validator/blob/develop/.github/workflows/test_with_pytest.yml>`_.

* Build docs
    This job checks that the Sphinx documentation builds correctly.
    This workflow is defined in `.github/workflows/verify_sphinx_doc.yml <https://github.com/iterorganization/IMAS-Validator/blob/develop/.github/workflows/verify_sphinx_doc.yml>`_.


Deployment
----------

* PyPI
  
New tagged releases are automatically build and distribution packages are uploaded on `PyPI <https://pypi.org/project/imas-validator/>`_. This workflow is defined in `.github/workflows/publish_pypi.yml <https://github.com/iterorganization/IMAS-Validator/blob/develop/.github/workflows/publish_pypi.yml>`_.

* ReadTheDocs

Each new updates on the ``develop`` and ``main`` branches are deployed automatically on ReadTheDocs, respectively in the `latest <https://imas-validator.readthedocs.io/en/latest/#>`_ and `stable <https://imas-validator.readthedocs.io/en/stable/#>`_ versions. 
