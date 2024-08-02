"""
This file describes the functions needed for the training course
"""

import imaspy
import numpy
from imaspy import DBEntry
from imaspy.ids_toplevel import IDSToplevel

# function for good db_entry
# function for bad db_entry


def training_core_profiles() -> IDSToplevel:
    cp = imaspy.IDSFactory("3.40.1").core_profiles()
    # Fill some properties:
    cp.ids_properties.homogeneous_time = 0  # INT_0D
    cp.ids_properties.comment = "Comment"  # STR_0D
    cp.ids_properties.provenance.node.resize(1)
    cp.ids_properties.provenance.node[0].path = "profiles_1d"  # STR_0D
    sources = ["First string", "Second string", "Third!"]
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
        temperature_fit_local = numpy.arange(4, dtype=numpy.int32)
        cp.profiles_1d[i].electrons.temperature_fit.measured = temperature_fit_local
        cp.profiles_1d[i].electrons.temperature_fit.local = temperature_fit_local
    return cp


def training_data_waves() -> IDSToplevel:
    wv = imaspy.IDSFactory("3.40.1").waves()
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
    with DBEntry("imas:hdf5?path=ids-validator-course/good", "w") as entry:
        entry.put(cp)
        entry.put(wv)
        print(entry.uri)
    cp.time = [1.0, 0.0]
    wv.time = [1.0, 0.0]
    with DBEntry("imas:hdf5?path=ids-validator-course/bad", "w") as entry:
        entry.put(cp)
        entry.put(wv)
        print(entry.uri)


if __name__ == "__main__":
    create_training_db_entries()
