from ids_validator.validate.validate import validate
from pathlib import Path

rulesets = ['test_ruleset']
ids_url = 'imas:mdsplus?' \
          'user=/home/ITER/wisznia/public/imasdb;' \
          'database=test;' \
          'pulse=1;' \
          'run=1;' \
          'version=3'

extra_rule_dirs = [Path('.')]
apply_generic = True

results = validate(rulesets, ids_url, extra_rule_dirs, apply_generic)
print(type(results))
print(results)
