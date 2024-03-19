#!/bin/bash
# Bamboo CI script for linting
# Note: this script should be run from the root of the git repository

# Debuggging:
set -e -o pipefail
echo "Loading modules..."

# Set up environment such that module files can be loaded
. /usr/share/Modules/init/sh
module purge
# Load modules required for linting
# - Python (obviously)
module load Python/3.8.6-GCCcore-10.2.0

# Debuggging:
echo "Done loading modules"
set -x

# Create a venv
rm -rf venv
python -m venv venv
. venv/bin/activate

# Install and run linters
pip install --upgrade .[linting]

black --check ids_validator
flake8 ids_validator --extend-ignore=E701,E704
mypy ids_validator
isort --check-only ids_validator
