from ids_validator.rules.loading import load_rules
from ids_validator.validate.result_collector import ResultCollector
from ids_validator.validate.validate import validate
from ids_validator.validate_options import RuleFilter, ValidateOptions

uri_list = [
    "imas:hdf5?path=/work/imas/shared/imasdb/ITER/3/130505/3",
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

    def setup(self, uri, ruleset):
        self.validate_options = ValidateOptions(
            rulesets=[ruleset],
        )

    def time_validate_full_run(self, uri, ruleset):
        validate(
            imas_uri=uri,
            validate_options=self.validate_options,
        )
    time_validate_full_run.timeout = 300


class NodeDict:
    params = uri_list

    def setup(self, uri):
        rule_filter = RuleFilter(name=["increasing_time"])
        self.validate_options = ValidateOptions(
            rule_filter=rule_filter,
            track_node_dict=True,
        )

    def time_validate_with_node_dict(self, uri):
        validate(
            imas_uri=uri,
            validate_options=self.validate_options,
        )
    time_validate_with_node_dict.timeout = 300


class LoadRules:
    def setup(self):
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
