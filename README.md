# README

# Set up your environment

# Developing

# Running test suite

# Linting

# User Workflow
- CLI
- Public API 
  - Data Entry
    - Options
      - IDS
      - Occ.
  - Ruleset
    - Which rulesets
    - Where to find defined rulesets
    - Whether to disable generic rulesets
- Execute
  - Load rules
  - Load data
  - Apply rules to data
    - Match rules with data
    - Loop over data
    - Get matching rules
    - Execute rules
    - Record successes and failures
- Report

# Examples
```
@validator("*")
def validate_ids_common(ids):
  Exists(
    ids.ids_properties.comment,
    ids.ids_properties.source,
    ids.ids_properties.provider,
  )
  if hasattr(ids, "time"):
    ids.time == Increasing()
        
@validator("*", min_dd_version="3.39.0")
def validate_ids_plugins_metadata(ids):
  plugins = ids.ids_properties.plugins
  plugins.node[:].path != ""
  plugins.node[:].put_operation[:].name != ""
  # etc.

@validator("gyrokinetics")
def validate_gyrokinetics_electron_definition(gk):
  # check electron definition
  for species in gk.species:
    if species.charge_norm != -1:
      continue
    species.mass_norm == 2.724437108e-4
    species.temperature_norm == 1.0
    species.density_norm == 1.0
    break
  else:
    error("No electron species found", gk.species)`
```