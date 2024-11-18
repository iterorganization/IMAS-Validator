import imaspy
import numpy
import pytest

from ids_validator.validate.ids_wrapper import IDSWrapper


def check_test_result(test, expected):
    assert isinstance(test, IDSWrapper)
    assert bool(test) is expected
    # TODO: test more properties of IDSWrapper


def test_cannot_wrap_wrapper():
    with pytest.raises(ValueError):
        IDSWrapper(IDSWrapper(1))


def test_validate_int_0d(test_data_core_profiles):
    homogeneous_time = test_data_core_profiles.ids_properties.homogeneous_time

    test = homogeneous_time == 0
    check_test_result(test, True)

    test = homogeneous_time == 1
    check_test_result(test, False)

    test = homogeneous_time > 1
    check_test_result(test, False)

    test = 1 < homogeneous_time
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


def test_validate_flt_0d(test_data_core_profiles):
    zmin = test_data_core_profiles.profiles_1d[0].ion[0].state[0].z_min
    zmax = test_data_core_profiles.profiles_1d[0].ion[0].state[0].z_max

    test = zmin == 1.0
    check_test_result(test, True)

    test = zmin < zmax
    check_test_result(test, True)

    test = -zmin < 0
    check_test_result(test, True)

    test = bool(zmin)
    assert test is True


# official DD has no CPX_0D nodes


def test_validate_str_0d(test_data_core_profiles):
    comment = test_data_core_profiles.ids_properties.comment

    test = comment == "Comment"
    check_test_result(test, True)

    test = bool(comment)
    assert test is True

    test = len(comment) == 3
    assert test is False

    test = "omm" in comment
    assert test is True

    # TODO: separate test module for method/property calls of wrapped objects
    test = comment.startswith("XYZ")
    check_test_result(test, False)


def test_validate_int_1d(test_data_waves):
    ntor = test_data_waves.coherent_wave[0].profiles_1d[0].n_tor

    test = (ntor == numpy.arange(10, dtype=numpy.int32)).all()
    check_test_result(test, True)

    test = (ntor == numpy.arange(10, dtype=numpy.int32)).any()
    check_test_result(test, True)

    test = (ntor == numpy.ones(10, dtype=numpy.int32)).all()
    check_test_result(test, False)

    test = (ntor == numpy.ones(10, dtype=numpy.int32)).any()
    check_test_result(test, True)

    test = len(ntor) == 10
    assert test is True

    test = 5 in ntor
    assert test is True

    test = 10 in ntor
    assert test is False

    test = ntor[4] == 4
    check_test_result(test, True)

    test = ntor[-1] == 9
    check_test_result(test, True)

    test = (ntor[2:5] == numpy.arange(2, 5, dtype=numpy.int32)).all()
    check_test_result(test, True)

    test = ntor == 1
    check_test_result(test, False)

    test = bool(ntor == numpy.ones(10, dtype=numpy.int32))
    assert test is False


def test_validate_flt_1d(test_data_core_profiles):
    rho_tor_norm = test_data_core_profiles.profiles_1d[0].grid.rho_tor_norm

    test = (rho_tor_norm == numpy.linspace(0.0, 1.0, 16)).all()
    check_test_result(test, True)

    test = (rho_tor_norm >= 0).all()
    check_test_result(test, True)

    test = len(rho_tor_norm) == 16
    assert test is True

    test = rho_tor_norm[-1] > rho_tor_norm[0]
    check_test_result(test, True)


def test_validate_cpx_1d(test_data_waves):
    e_field_plus = test_data_waves.coherent_wave[0].full_wave[0].e_field.plus[0].values

    test = e_field_plus == [1, 1j, -1, -1j]
    check_test_result(test, True)

    test = e_field_plus.real == numpy.array([1, 0, -1, 0])
    check_test_result(test, True)

    test = e_field_plus.imag == numpy.array([0, 1, 0, -1])
    check_test_result(test, True)

    test = len(e_field_plus) == 4
    assert test is True


def test_validate_str_1d(test_data_core_profiles):
    sources = test_data_core_profiles.ids_properties.provenance.node[0].sources

    test = sources == ["First string", "Second string", "Third!"]
    check_test_result(test, True)

    test = len(sources) == 3
    assert test is True

    test = len(sources[1]) == 6
    assert test is False

    test = len(sources[-1]) == 6
    assert test is True

    test = "Third!" in sources
    assert test is True


def test_validate_flt_2d(test_data_waves):
    pdnt = test_data_waves.coherent_wave[0].profiles_1d[0].power_density_n_tor

    test = pdnt[0] == [1.0, 2.0, 3.0]
    check_test_result(test, True)

    test = pdnt[1, :] == [4.0, 5.0, 6.0]
    check_test_result(test, True)

    test = len(pdnt) == 2
    assert test is True

    test = len(pdnt[0]) == 3
    assert test is True

    test = pdnt > 0
    check_test_result(test, True)

    test = pdnt == [1, 2, 3]
    check_test_result(test, False)


def test_validate_flt_3d(test_data_waves):
    pdnt = test_data_waves.coherent_wave[0].profiles_2d[0].power_density_n_tor

    test = pdnt[0, :, 0].size == 3
    check_test_result(test, True)

    test = pdnt.size == 24
    check_test_result(test, True)

    test = pdnt[1] > 4
    check_test_result(test, True)

    test = pdnt[1] == [[2.0, 3.0, 4.0, 5.0]]
    check_test_result(test, False)


def test_bool_non_numpy_array():
    cp = imaspy.IDSFactory().core_profiles()
    cp.time = [1, 2, 3]
    wrapper = IDSWrapper(cp)
    assert bool(wrapper.time) is True


def test_transfer_ids_nodes_between_arrays():
    wrapper = IDSWrapper([1, 2, 3], ids_nodes=['a'])
    index = IDSWrapper(0, ids_nodes=['b'])
    assert wrapper[0]._ids_nodes == ['a']
    assert wrapper[index]._ids_nodes == ['a', 'b']
    assert not isinstance([1, 2, 3][index], IDSWrapper)
