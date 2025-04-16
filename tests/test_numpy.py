import numpy

from imas_validator.validate.ids_wrapper import IDSWrapper


def test_idswrapper_ufunc(test_data_core_profiles):
    rho_tor_norm = test_data_core_profiles.profiles_1d[0].grid.rho_tor_norm

    # Ufunc from operation
    result = numpy.array(0) + rho_tor_norm
    assert isinstance(result, IDSWrapper)
    assert result._ids_nodes == rho_tor_norm._ids_nodes
    assert result == rho_tor_norm

    # Eplicit ufuncs
    result = numpy.add(rho_tor_norm, 0)
    assert isinstance(result, IDSWrapper)
    assert result._ids_nodes == rho_tor_norm._ids_nodes
    assert result == rho_tor_norm

    result = numpy.add.reduce(rho_tor_norm)
    assert isinstance(result, IDSWrapper)
    assert result._ids_nodes == rho_tor_norm._ids_nodes
    assert result == sum(rho_tor_norm._obj.value)

    # This is a standard Python function
    result = sum(rho_tor_norm)
    assert isinstance(result, IDSWrapper)
    # result._ids_nodes has len(rho_tor_norm) items, one for each element that was added
    assert {id(n) for n in result._ids_nodes} == {
        id(n) for n in rho_tor_norm._ids_nodes
    }
    assert result == sum(rho_tor_norm._obj.value)

    # Numpy public API functions
    result = numpy.sum(rho_tor_norm)
    assert isinstance(result, IDSWrapper)
    assert result._ids_nodes == rho_tor_norm._ids_nodes
    assert result == sum(rho_tor_norm._obj.value)

    result = numpy.mean(rho_tor_norm)
    assert isinstance(result, IDSWrapper)
    assert result._ids_nodes == rho_tor_norm._ids_nodes
    assert result == numpy.mean(rho_tor_norm._obj.value)
