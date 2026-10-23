# AGENTS.md

This file provides guidance to AI coding assistants working with code in this repository.

## What this is

IMAS-Validator validates IMAS IDS data (read through `imas-python`) against validation rules written as plain Python functions using `assert`. The CLI entry point is `imas_validator` (`imas_validator/cli/imas_validator_cli.py:execute_cli`), with two subcommands: `validate <uri>` (run rules against a data entry and write JUnit XML/TXT/HTML reports) and `explore` (list the available rulesets and rule docstrings).

## Commands

Use a local `venv/` (already present in the checkout). Install with `pip install -e .[all]` (or `.[test]`, `.[linting]`, `.[docs]`, `.[benchmark]`).

Tests (run from the repo root, because tests refer to `tests/rulesets/...` by relative path; CI sets `IMAS_VERSION=3.40.1`):
```bash
IMAS_VERSION=3.40.1 python -m pytest -n=auto            # full suite (pytest-xdist)
python -m pytest tests/test_loading.py::test_name        # single test
python -m pytest -p no:randomly ...                      # disable pytest-randomly ordering
```
The root `conftest.py` removes `RULESET_PATH` from the environment and provides `test_data_core_profiles` / `test_data_waves` fixtures (IDSWrapper-wrapped IDSs from DD 3.40.1).

Linting (CI runs all four on `imas_validator/` only):
```bash
black --check imas_validator     # black pinned to >=24,<25
flake8 imas_validator            # max line length 88, config in setup.cfg
mypy imas_validator              # strict: disallow untyped defs/calls/decorators; tests and assets excluded
isort --check-only imas_validator
```

Docs: `make -C docs html` (Sphinx). Benchmarks: `asv` with `asv.conf.json`, benchmarks live in `benchmarks/`.

The version comes from git tags via setuptools_scm and is written to `imas_validator/_version.py`. That file is generated; don't edit it. PRs target the `develop` branch.

## Architecture

The pipeline (`validate/validate.py:validate`): open an `imas.DBEntry` → `ResultCollector` → `load_rules` → `RuleExecutor.apply_rules_to_data` → `IDSValidationResultCollection` → report generators in `report/`.

**Rule discovery** (`rules/loading.py`): a *rule directory* contains *ruleset* subdirectories (for example `generic`, `iter`, `scenarios`), and each ruleset contains rule `.py` files. Rule directories come from three sources: the bundled `imas_validator/assets/rulesets/` (unless `use_bundled_rulesets=False`), `ValidateOptions.extra_rule_dirs`, and the colon-separated `RULESET_PATH` env var. The `generic` ruleset is applied by default (`apply_generic`). Other rulesets are applied only when named in `ValidateOptions.rulesets`, or when a `RuleFilter.name` token equals the ruleset name (optionally followed by `/...`), or all of them in explore mode when no ruleset is named. A ruleset's `__init__.py` holds only its docstring and is never loaded as rules. `RuleFilter` then filters individual rules: `name` tokens are substrings of the rule name, `ids` entries must exactly match one of the rule's IDS names. On the CLI, `--filter` sends IDS names to `ids` and other strings to `name` (`common/utils.py:prepare_rule_filter_object`). Multi-value options (`-r`, `-e`, `-f`, `--filter_*`) use `nargs="+"`, so they must follow the `validate` URIs.

**Rule files are not imported as modules.** `rules/ast_rewrite.py:run_path` reads the source, uses an AST transformer to rewrite every `assert x, msg` statement into a call `assert(x, msg)`, and then `exec`s it with injected globals: `validator` (a per-file `ValidatorRegistry.validator` decorator), `assert` (bound to `ResultCollector.assert_`), and the helpers from `rules/helpers.py` (`Select`, `Increasing`, `Decreasing`, `Approx`, `Parent`, exported through `__all__`/`HELPER_DICT`). This is why rule files use undefined names (flake8 F821 is ignored for `imas_validator/assets/*`) and why mypy ignores assets. To add a new helper for rule authors, add it to `__all__` in `helpers.py`.

**`@validator(*ids_names, version="")`** (`rules/data.py`) creates `IDSValidationRule`s. IDS names can be `"*"` or `"name:occurrence"`. Multi-IDS rules must give an occurrence for every name. `version` is a `packaging` SpecifierSet that is matched against the IDS's DD version. A rule's name is `ruleset/file.py:func`.

**Execution** (`validate/rule_executor.py`): for each IDS occurrence in the entry, the executor loads it with `autoconvert=False`, matches rules on the *first* IDS name and occurrence, and for multi-IDS rules also loads the additional IDSs. An exception inside a rule becomes an error result, not a crash. With `use_pdb`, a failed assert raises `InternalValidateDebugException` and the executor drops into `pdb.post_mortem` at the rule's own frame.

**IDSWrapper** (`validate/ids_wrapper.py`): each IDS passed to a rule is wrapped. Attribute access, indexing, operators and numpy ufuncs all return new `IDSWrapper`s that accumulate the list of `IDSPrimitive` nodes they touched (`_ids_nodes`). When `assert_` receives a wrapper, it records those nodes, so failure reports can name the exact IDS paths involved. Wrapper semantics must be preserved when you change operators or helpers.

**Node coverage** (`validate/result_collector.py`, enabled by `track_node_dict` / CLI `-nc`): the collector compares the nodes visited by asserts with all filled leaf paths of each IDS (`_iter_filled_paths`, which carries AoS indices down the tree and uses `iter_nonempty_` so that lazy-loaded IDSs are rejected). It produces a `CoverageMap(filled, visited, overlap)` for each IDS.

## Test rulesets

`tests/rulesets/*` are fixture rule directories (for example `base`, `env_var`, `filter_test`, `validate-test`, and `exceptions`, which contains deliberately broken files). Tests point `extra_rule_dirs` or `RULESET_PATH` at these directories.
