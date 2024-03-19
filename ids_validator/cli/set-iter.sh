#!/bin/bash
 
export PYTHONPATH=$PYTHONPAT:`pwd`/../../
export RULESET_PATH=`pwd`/../../tests/rulesets/env_var

. ../../venv/bin/activate

module load IMAS/3.40.1-5.1.0-foss-2020b
module load IMASPy/1.0.0-foss-2020b
