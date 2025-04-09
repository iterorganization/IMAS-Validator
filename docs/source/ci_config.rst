.. _`ci configuration`:

CI configuration
================

imas-validator uses `ITER Bamboo <https://ci.iter.org/>`_ for CI. This page provides an overview
of the CI Plan and deployment projects.

CI Plan
-------

The `imas-validator CI plan <https://ci.iter.org/browse/IMEX-IVALID>`_ consists of 3 types of jobs:

Linting 
    Run ``black``, ``flake8``, ``mypy`` and ``isort`` on the imas-validator code base.
    See :ref:`code style and linting`.

    The CI script executed in this job is ``ci/linting.sh``.

Testing
    This runs all unit tests with pytest.

    The CI script executed in this job is ``ci/run_pytest.sh``, which expects the
    modules it needs to load as arguments.

Build docs
    This job builds the Sphinx documentation.

    The CI script executed in this job is: ``ci/build_docs.sh``, which expects the
    modules it needs to load as arguments.


Deployment projects
-------------------

There is currently one Bamboo deployment project for imas-validator:

`Deploy imas-validator-Doc <https://ci.iter.org/deploy/viewDeploymentProjectEnvironments.action?id=1908899843>`_
    Deploy the documentation created in the `Build docs` job to `Sharepoint
    <https://sharepoint.iter.org/departments/POP/CM/IMDesign/Code%20Documentation/imas-validator/index.html#>`_.

    This deployment project runs for after each successful CI build of the IMAS-Validator main
    branch.
