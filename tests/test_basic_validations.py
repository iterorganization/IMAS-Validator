import imaspy
import numpy
import pytest

# from ids_validator.validate.ids_wrapper import IDSWrapper
IDSWrapper = object()

# Until this functionality is implemented, everything in this module will fail
pytestmark = pytest.mark.xfail(strict=True)


@pytest.fixture
def core_profiles():
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
def waves():
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


def check_test_result(test, expected):
    assert isinstance(test, IDSWrapper)
    assert bool(test) is expected
    # TODO: test more properties of IDSWrapper


def test_validate_int_0d(core_profiles):
    homogeneous_time = core_profiles.ids_properties.homogeneous_time

    test = homogeneous_time == 0
    check_test_result(test, True)

    test = homogeneous_time == 1
    check_test_result(test, False)

    test = homogeneous_time > 1
    check_test_result(test, False)

    test = 0 <= homogeneous_time <= 2
    check_test_result(test, True)

    # These cannot be wrapped in an IDSWrapper, just check expected outcome ok:
    test = bool(homogeneous_time)
    assert test is False

    test = not homogeneous_time
    assert test is True

    test = homogeneous_time in [0, 1, 2]
    assert test is True


def test_validate_str_0d(core_profiles):
    comment = core_profiles.ids_properties.comment

    test = comment == "Comment"
    check_test_result(test, True)

    test = bool(comment)
    assert test is True

    # TODO: check if len may return an IDSWrapper...
    test = len(comment) == 3
    check_test_result(test, False)

    test = "omm" in comment
    check_test_result(test, True)

    test = comment.startswith("XYZ")
    check_test_result(test, False)


# TODO:

# Other 0D values
# def test_validate_flt_0d
# NOTE: in the official DD there are no CPX_0D nodes.. let's skip this
# ~~def test_validate_cpx_0d~~

# 1D data types:
# def test_validate_str_1d
# def test_validate_int_1d
# def test_validate_flt_1d
# def test_validate_cpx_1d

# Test 1 or 2 higher dimensional types (FLT_2D and FLT_3D?), they use the same
# underlying objects (IDSWrapper -> IDSNumericArray -> numpy.ndarray) so shouldn't
# behave different compared to the 1D data types
