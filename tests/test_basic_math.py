import numpy
import pytest

# from ids_validator.validate.ids_wrapper import IDSWrapper
IDSWrapper = object()
# from ids_validator.rules.exceptions import DoubleWrapError
DoubleWrapError = ValueError

# Until this functionality is implemented, everything in this module will fail
pytestmark = pytest.mark.xfail(strict=True)


def check_test_result(test, expected):
    assert isinstance(test, IDSWrapper)
    assert bool(test) is expected


def test_validate_int_0d(test_data_core_profiles):
    homogeneous_time = test_data_core_profiles.ids_properties.homogeneous_time

    test = 1 + homogeneous_time == 1
    check_test_result(test, True)

    test = homogeneous_time + 1 == 1
    check_test_result(test, True)


def test_validate_flt_0d(test_data_core_profiles):
    zmin = test_data_core_profiles.profiles_1d[0].ion[0].state[0].z_min
    zmax = test_data_core_profiles.profiles_1d[0].ion[0].state[0].z_max

    test = zmin == 1.0 + 1e-16
    check_test_result(test, True)

    test = zmin == 1.0 + 1e-15
    check_test_result(test, False)

    test = zmax - zmin > 0
    check_test_result(test, False)


@pytest.mark.skip(reason="official DD has no CPX_0D nodes")
def test_validate_cpx_0d(test_data_waves):
    pass


def test_validate_str_0d(test_data_core_profiles):
    comment = test_data_core_profiles.ids_properties.comment

    test = comment + "hi" == "Commenthi"
    check_test_result(test, True)


def test_validate_int_1d(test_data_waves):
    ntor = test_data_waves.ntor

    test = (ntor + 5 == numpy.arange(5, 15, dtype=numpy.int32)).any()
    check_test_result(test, False)


def test_validate_flt_1d(test_data_core_profiles):
    rho_tor_norm = test_data_core_profiles.profiles_id[0].grid.rho_tor_norm

    test = numpy.allclose(rho_tor_norm + 1e-15, numpy.linspace(0.0, 1.0, 16))
    check_test_result(test, True)


def test_validate_cpx_1d(test_data_waves):
    e_field_plus = test_data_waves.coherent_wave[0].full_wave[0].e_field.plus[0].values

    test = e_field_plus[1] + 1 == 1 + 1j
    check_test_result(test, True)

    test = e_field_plus[1] * 1j == -1 + 0j
    check_test_result(test, True)

    test = abs(e_field_plus[0] + 1j) == numpy.sqrt(2)
    check_test_result(test, True)


def test_validate_str_1d(test_data_core_profiles):
    sources = test_data_core_profiles.ids_properties.provenance.node[0].sources

    test = sources + ["hi"] == ["First string", "Second string", "Third!", "hi"]
    assert test is True


def test_validate_flt_2d(test_data_core_profiles):
    pass


def test_validate_flt_3d(test_data_core_profiles):
    pass
