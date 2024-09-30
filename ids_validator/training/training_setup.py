"""
This file describes the functions needed for the training course
"""

import os
import shutil
from pathlib import Path

import imaspy
import numpy
from imaspy import DBEntry
from imaspy.ids_toplevel import IDSToplevel

from ids_validator import get_project_root


def training_core_profiles(new_version: bool = False) -> IDSToplevel:
    if new_version:
        version = "3.42.0"
    else:
        version = "3.40.1"
    cp = imaspy.IDSFactory(version).core_profiles()
    # Fill some properties:
    cp.ids_properties.homogeneous_time = 0  # INT_0D
    cp.ids_properties.comment = "Comment"  # STR_0D
    cp.ids_properties.provenance.node.resize(1)
    cp.ids_properties.provenance.node[0].path = "profiles_1d"  # STR_0D
    sources = ["First string", "Second string", "Third!"]
    if new_version:
        timestamp = "2020-07-24T14:19:00Z"
        cp.ids_properties.provenance.node[0].reference.resize(3)
        for i in range(3):
            cp.ids_properties.provenance.node[0].reference[i].name = sources[i]
            cp.ids_properties.provenance.node[0].reference[i].timestamp = timestamp
    else:
        cp.ids_properties.provenance.node[0].sources = sources  # STR_1D
    # Fill some data
    cp.time = [0.0, 1.0]
    cp.profiles_1d.resize(2)
    for i in range(2):
        cp.profiles_1d[i].time = cp.time[i]
        cp.profiles_1d[i].grid.rho_tor_norm = numpy.linspace(0.0, 1.0, 16)  # FLT_1D
        cp.profiles_1d[i].ion.resize(1)
        cp.profiles_1d[i].ion[0].state.resize(1)
        cp.profiles_1d[i].ion[0].state[0].z_min = 1.0  # FLT_0D
        cp.profiles_1d[i].ion[0].state[0].z_average = 1.25  # FLT_0D
        cp.profiles_1d[i].ion[0].state[0].z_max = 1.5  # FLT_0D
        cp.profiles_1d[i].ion[0].density = numpy.ones(16)
        cp.profiles_1d[i].ion[0].z_ion = 1 + 1e-8
        cp.profiles_1d[i].ion[0].element.resize(1)
        cp.profiles_1d[i].ion[0].element[0].z_n = 2
        cp.profiles_1d[i].ion[0].element[0].atoms_n = 1
        temperature_fit_local = numpy.arange(4, dtype=numpy.int32)
        cp.profiles_1d[i].electrons.temperature_fit.measured = temperature_fit_local
        cp.profiles_1d[i].electrons.temperature_fit.local = temperature_fit_local
        cp.profiles_1d[i].electrons.density = numpy.ones(16)
    return cp


def training_data_waves(new_version: bool = False) -> IDSToplevel:
    if new_version:
        version = "3.42.0"
    else:
        version = "3.40.1"
    wv = imaspy.IDSFactory(version).waves()
    # Fill some properties:
    wv.ids_properties.homogeneous_time = 0  # INT_0D
    # Fill some data
    wv.time = [0.0, 1.0]
    wv.coherent_wave.resize(2)
    for i in range(2):
        wv.coherent_wave[i].profiles_1d.resize(1)
        p1d = wv.coherent_wave[i].profiles_1d[0]
        p1d.time = wv.time[i]
        n_tor_size = 10
        p1d.n_tor = numpy.arange(n_tor_size, dtype=numpy.int32)  # INT_1D
        p1d.grid.rho_tor_norm = numpy.arange(n_tor_size, dtype=numpy.int32)
        p1d.power_density = numpy.random.random(n_tor_size)  # FLT_1D
        p1d.power_density_n_tor = numpy.random.random(
            (n_tor_size, n_tor_size)
        )  # FLT_2D
        wv.coherent_wave[i].profiles_2d.resize(1)
        value = numpy.arange(24, dtype=float).reshape((2, 3, 4))
        wv.coherent_wave[i].profiles_2d[0].time = wv.time[i]
        wv.coherent_wave[i].profiles_2d[0].grid.r = numpy.arange((6)).reshape(
            (2, 3)
        )  # FLT_3D
        wv.coherent_wave[i].profiles_2d[0].n_tor = value[0, 0, :]  # FLT_3D
        wv.coherent_wave[i].profiles_2d[0].power_density_n_tor = value  # FLT_3D
        wv.coherent_wave[i].full_wave.resize(1)
        wv.coherent_wave[i].full_wave[0].time = wv.time[i]
        wv.coherent_wave[i].full_wave[0].e_field.plus.resize(1)
        wv.coherent_wave[i].full_wave[0].e_field.plus[0].values = [
            1,
            1j,
            -1,
            -1j,
        ]  # CPX_1D
    return wv


def create_training_db_entries() -> None:
    cp = training_core_profiles()
    wv = training_data_waves()
    with DBEntry(
        "imas:hdf5?path=ids-validator-course/good", "w", dd_version="3.40.1"
    ) as entry:
        entry.put(cp)
        entry.put(wv)
        print(entry.uri)
    cp.time = [1.0, 0.0]
    wv.time = [1.0, 0.0]
    with DBEntry(
        "imas:hdf5?path=ids-validator-course/bad", "w", dd_version="3.40.1"
    ) as entry:
        entry.put(cp)
        entry.put(wv)
        print(entry.uri)
    with DBEntry(
        "imas:hdf5?path=ids-validator-course/new", "w", dd_version="3.42.0"
    ) as entry:
        cp = training_core_profiles(new_version=True)
        wv = training_data_waves(new_version=True)
        entry.put(cp)
        entry.put(wv)
        print(entry.uri)


def copy_training_tests_to_cwd() -> None:
    training_rule_dir = (
        get_project_root() / "ids_validator" / "assets" / "rulesets" / "custom_ruleset"
    )
    shutil.copytree(
        training_rule_dir,
        Path(os.getcwd()) / "ids-validator-training-rulesets" / "custom_ruleset",
        dirs_exist_ok=True,
    )


if __name__ == "__main__":
    create_training_db_entries()
    copy_training_tests_to_cwd()
