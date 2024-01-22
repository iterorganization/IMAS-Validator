import imaspy
import numpy
import pytest

# from ids_validator.validate.ids_wrapper import IDSWrapper
IDSWrapper = object()
# from ids_validator.rules.exceptions import DoubleWrapError
DoubleWrapError = ValueError

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


def test_cannot_wrap_wrapper():
    with pytest.raises(DoubleWrapError):
        IDSWrapper(IDSWrapper(1))


def test_validate_int_0d(core_profiles):
    homogeneous_time = core_profiles.ids_properties.homogeneous_time

    test = homogeneous_time == 0
    check_test_result(test, True)

    test = homogeneous_time == 1
    check_test_result(test, False)

    test = homogeneous_time > 1
    check_test_result(test, False)

    test = 1 > homogeneous_time
    check_test_result(test, False)

    # These cannot be wrapped in an IDSWrapper, just check expected outcome ok:
    test = bool(homogeneous_time)
    assert test is False

    test = not homogeneous_time
    assert test is True

    test = homogeneous_time in [0, 1, 2]
    assert test is True

    test = 0 <= homogeneous_time <= 2
    assert test is True


def test_validate_flt_0d(core_profiles):
    zmin = core_profiles.profiles_1d[0].ion[0].state[0].z_min
    zmax = core_profiles.profiles_1d[0].ion[0].state[0].z_max

    test = zmin == 1.0
    check_test_result(test, True)

    test = zmin < zmax
    check_test_result(test, False)

    test = -zmin < 0
    check_test_result(test, True)

    test = bool(zmin)
    check_test_result(test, True)


@pytest.mark.skip(reason="official DD has no CPX_0D nodes")
def test_validate_cpx_0d(waves):
    pass


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


def test_validate_int_1d(waves):
    ntor = waves.ntor

    test = (ntor == numpy.arange(10, dtype=numpy.int32)).all()
    check_test_result(test, True)

    test = (ntor == numpy.arange(10, dtype=numpy.int32)).any()
    check_test_result(test, True)

    test = (ntor == numpy.ones(10, dtype=numpy.int32)).all()
    check_test_result(test, False)

    test = (ntor == numpy.ones(10, dtype=numpy.int32)).any()
    check_test_result(test, True)

    test = len(ntor) == 10
    check_test_result(test, True)

    test = 5 in ntor
    check_test_result(test, True)

    test = 10 in ntor
    check_test_result(test, False)

    test = ntor[4] == 4
    check_test_result(test, True)

    test = ntor[-1] == 9
    check_test_result(test, True)

    test = (ntor[2:5] == numpy.arange(2, 5, dtype=numpy.int32)).all()
    check_test_result(test, True)

    with pytest.raises(ValueError):
        ntor == numpy.arange(9)


def test_validate_flt_1d(core_profiles):
    rho_tor_norm = core_profiles.profiles_id[0].grid.rho_tor_norm

    test = (rho_tor_norm == numpy.linspace(0.0, 1.0, 16)).all()
    check_test_result(test, True)

    test = (rho_tor_norm >= 0).all()
    check_test_result(test, True)

    test = len(rho_tor_norm) == 16
    check_test_result(test, True)

    test = rho_tor_norm[-1] > rho_tor_norm[0]
    check_test_result(test, True)


def test_validate_cpx_1d(waves):
    e_field_plus = waves.coherent_wave[0].full_wave[0].e_field.plus[0].values

    test = e_field_plus == [1, 1j, -1, -1j]
    check_test_result(test, True)

    test = e_field_plus.real == numpy.array([1, 0, -1, 0])
    check_test_result(test, True)

    test = e_field_plus.imag == numpy.array([0, 1, 0, -1])
    check_test_result(test, True)

    test = len(e_field_plus) == 4
    check_test_result(test, True)


def test_validate_str_1d(core_profiles):
    sources = core_profiles.ids_properties.provenance.node[0].sources

    test = sources == ["First string", "Second string", "Third!"]
    check_test_result(test, True)

    test = len(sources) == 3
    check_test_result(test, True)

    test = len(sources[1]) == 6
    check_test_result(test, False)

    test = len(sources[-1]) == 6
    check_test_result(test, True)

    test = "Third!" in sources
    assert test is True


def test_validate_flt_2d(waves):
    pdnt = waves.coherent_wave[0].profiles_1d[0].power_density_n_tor

    test = pdnt[0] == [1.0, 2.0, 3.0]
    check_test_result(test, True)

    test = pdnt[1, :] == [4.0, 5.0, 6.0]
    check_test_result(test, True)

    test = len(pdnt) == 2
    check_test_result(test, True)

    test = len(pdnt[0]) == 3
    check_test_result(test, True)


def test_validate_flt_3d(waves):
    pdnt = waves.coherent_wave[0].profiles_2d[0].power_density_n_tor

    test = pdnt[0, :, 0].size == 3
    check_test_result(test, True)

    test = pdnt.size == 24
    check_test_result(test, True)


# TODO:
# Test 1 or 2 higher dimensional types (FLT_2D and FLT_3D?), they use the same
# underlying objects (IDSWrapper -> IDSNumericArray -> numpy.ndarray) so shouldn't
# behave different compared to the 1D data types
# broadcasting
