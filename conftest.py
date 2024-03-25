from unittest.mock import Mock
import numpy
import pytest
import imaspy

from ids_validator.validate.ids_wrapper import IDSWrapper


@pytest.fixture
def test_data_core_profiles():
    cp = imaspy.IDSFactory("3.40.1").core_profiles()
    # Fill some properties:
    cp.ids_properties.homogeneous_time = 0  # INT_0D
    cp.ids_properties.comment = "Comment"  # STR_0D
    cp.ids_properties.provenance.node.resize(1)
    cp.ids_properties.provenance.node[0].path = "profiles_1d"  # STR_0D
    sources = ["First string", "Second string", "Third!"]
    cp.ids_properties.provenance.node[0].sources = sources  # STR_1D
    # Fill some data
    cp.profiles_1d.resize(1)
    cp.profiles_1d[0].grid.rho_tor_norm = numpy.linspace(0.0, 1.0, 16)  # FLT_1D
    cp.profiles_1d[0].ion.resize(1)
    cp.profiles_1d[0].ion[0].state.resize(1)
    cp.profiles_1d[0].ion[0].state[0].z_min = 1.0  # FLT_0D
    cp.profiles_1d[0].ion[0].state[0].z_average = 1.25  # FLT_0D
    cp.profiles_1d[0].ion[0].state[0].z_max = 1.5  # FLT_0D
    temperature_fit_local = numpy.arange(4, dtype=numpy.int32)
    cp.profiles_1d[0].electrons.temperature_fit.local = temperature_fit_local
    # And wrap it:
    return IDSWrapper(cp)


@pytest.fixture
def test_data_waves():
    wv = imaspy.IDSFactory("3.40.1").waves()
    # Fill some properties:
    wv.ids_properties.homogeneous_time = 0  # INT_0D
    # Fill some data
    wv.coherent_wave.resize(1)
    wv.coherent_wave[0].profiles_1d.resize(1)
    p1d = wv.coherent_wave[0].profiles_1d[0]
    p1d.n_tor = numpy.arange(10, dtype=numpy.int32)  # INT_1D
    p1d.power_density = numpy.random.random(10)  # FLT_1D
    p1d.power_density_n_tor = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]  # FLT_2D
    wv.coherent_wave[0].profiles_2d.resize(1)
    value = numpy.arange(24, dtype=float).reshape((2, 3, 4))
    wv.coherent_wave[0].profiles_2d[0].power_density_n_tor = value  # FLT_3D
    wv.coherent_wave[0].full_wave.resize(1)
    wv.coherent_wave[0].full_wave[0].e_field.plus.resize(1)
    wv.coherent_wave[0].full_wave[0].e_field.plus[0].values = [1, 1j, -1, -1j]  # CPX_1D
    # And wrap it:
    return IDSWrapper(wv)


@pytest.fixture
def test_logger():
    logger = Mock()
    return logger
