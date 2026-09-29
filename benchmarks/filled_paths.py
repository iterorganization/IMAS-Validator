"""Synthetic coverage benchmark; no external database is required."""

import imas

from imas_validator.validate.result_collector import ResultCollector
from imas_validator.validate_options import ValidateOptions


class FilledPaths:
    params = [100, 1_000, 10_000]
    param_names = ["size"]

    def setup(self, size):
        self.ids = imas.IDSFactory("3.40.1").core_profiles()
        self.ids.profiles_1d.resize(size)
        for index, profile in enumerate(self.ids.profiles_1d):
            profile.time = float(index)
            profile.ion.resize(2)
            for ion in profile.ion:
                ion.temperature = [1.0]
                ion.density = [2.0]

    def time_collect_filled_paths(self, size):
        # A fresh collector prevents repeat measurements from timing a cache hit.
        collector = ResultCollector(ValidateOptions(track_node_dict=True), "")
        collector.append_nodes_dict({}, [(self.ids, "core_profiles", 0)])

    def peakmem_collect_filled_paths(self, size):
        self.time_collect_filled_paths(size)
