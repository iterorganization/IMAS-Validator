from ids_validator.rules.loading import load_rules
from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.validate import validate
from ids_validator.validate_options import RuleFilter, ValidateOptions
from ids_validator.training.training_setup import create_training_db_entries

uri_list = [
    "imas:hdf5?path=ids-validator-course/good",
    "imas:hdf5?user=public;pulse=105053;run=1;database=ITER;version=3",
]

generic_ruleset_list = [
    "generic",
    "iter",
    "scenarios",
]


class FullValidate:
    params = [
        uri_list,
        generic_ruleset_list,
    ]

    # param_names = ["uri", "ruleset"]

    def setup(self, uri, ruleset):
        create_training_db_entries()
        self.validate_options = ValidateOptions(
            rulesets=[ruleset],
        )

    def time_validate_full_run(self, uri, ruleset):
        validate(
            imas_uri=[uri],
            validate_options=self.validate_options,
        )


class NodeDict:
    params = [
        uri_list,
    ]

    # param_names = ["uri"]

    def setup(self, uri):
        create_training_db_entries()
        rule_filter = RuleFilter(name=["increasing_time"])
        self.validate_options = ValidateOptions(
            rule_filter=rule_filter,
            track_node_dict=True,
        )

    def time_validate_with_node_dict(self, uri):
        validate(
            imas_uri=[uri],
            validate_options=self.validate_options,
        )


class LoadRules:
    def setup(self):
        create_training_db_entries()
        self.validate_options = ValidateOptions()
        self.result_collector = ResultCollector(
            validate_options=self.validate_options,
            imas_uri=uri_list[0],
        )

    def time_load_rules(self):
        load_rules(
            result_collector=self.result_collector,
            validate_options=self.validate_options,
        )


# how many URIs?
# test full run
#     - per ruleset?
#     - all tests
# test only run not ids load?
# test node dict
#     - few specific tests?
# test load rules
