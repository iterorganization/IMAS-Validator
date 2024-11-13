"""Rules applying to all IDSs containing GGDs"""

import re

import imaspy
from imaspy import identifiers
from imaspy.ids_data_type import IDSDataType
from imaspy.ids_defs import IDS_TIME_MODE_HOMOGENEOUS

SUPPORTED_IDS_NAMES = (
    "edge_profiles",
    "edge_sources",
    "edge_transport",
    "mhd",
    "radiation",
    "runaway_electrons",
    "wall",
)

# TODO: Some IDSs do not have the grid structure in a separate `grid_ggd` object, as
# described by the GGD guidelines. They are currently not covered by the validations.
# If the DD for these IDSs stays like this, they will need to be handled separately.
# GGD grid locations for each IDS:
# equilibrium (grids_ggd/grid)
# distribution_sources (source/ggd/grid)
# distributions (distribution/ggd/grid)
# tf (field_map/grid)
# transport_solver_numerics (boundary_conditions_ggd/grid)
# waves (coherent_wave/full_wave/grid)


# Helper functions
def assert_homogeneous_time_mode(ids):
    assert ids.ids_properties.homogeneous_time == IDS_TIME_MODE_HOMOGENEOUS


def multi_validator(ids_names):
    """Decorator to apply the @validator decorator for multiple IDSs."""

    def decorator(func):
        for name in ids_names:
            func = validator(name)(func)
        return func

    return decorator


def assert_identifier_filled(identifier):
    """Asserts that an identifier has its name, index and description fields filled."""
    assert identifier.name.has_value
    assert identifier.index.has_value
    assert identifier.description.has_value


def assert_index_in_aos_identifier(aos, index):
    """Asserts that a given index appears exactly once in the index identifiers of
    a structure of an AoS."""
    matches = sum(1 for structure in aos if structure.identifier.index == index)
    assert matches == 1


def find_structure_by_index(aos, index):
    """Return the first object in an AoS whose identifier.index matches the
    given index, or None if no match is found."""
    for structure in aos:
        if structure.identifier.index == index:
            return structure


def is_index_in_identifier_ref(index, identifier_ref):
    """Checks if a given index appears in an identifier reference."""
    return any(index == member.value for member in identifier_ref)


def recursive_ggd_path_search(quantity, scalar_list, vector_list):
    """Recursively searches through an IDS node for scalar GGD arrays
    (real & complex) and vector GGD arrays (regular and rphiz), and stores
    these in the scalar and vector lists, respectively.
    """
    for subquantity in quantity:
        if subquantity.metadata.data_type == IDSDataType.STRUCT_ARRAY:
            # Get scalar and complex scalar array quantities
            if (
                subquantity.metadata.structure_reference
                in [
                    "generic_grid_scalar",
                    "generic_grid_scalar_complex",
                ]
                and subquantity.has_value
            ):
                scalar_list.append(subquantity)

            # Get vector and rzphi-vector array quantities
            # From DDv4 onward `generic_grid_vector_components_rzphi` will be
            # replaced by `generic_grid_vector_components_rphiz`
            elif (
                subquantity.metadata.structure_reference
                in [
                    "generic_grid_vector_components",
                    "generic_grid_vector_components_rzphi",
                    "generic_grid_vector_components_rphiz",
                ]
                and subquantity.has_value
            ):
                vector_list.append(subquantity)

        if subquantity.metadata.data_type == IDSDataType.STRUCTURE:
            recursive_ggd_path_search(
                subquantity,
                scalar_list,
                vector_list,
            )


def get_ggd_aos(ids):
    """Get a list containing all GGD AoS nodes in the IDS"""
    ggd_list = []
    for node in Select(ids, "(^|/)ggd$", leaf_only=False):
        if node.metadata.name == "ggd":
            parent_node = imaspy.util.get_parent(node._obj)
            # Do not include structures of GGD, i.e. ggd[0]
            if parent_node.metadata.name != "ggd":
                ggd_list.append(node)
    return ggd_list


def get_matching_grid_ggd(ids, array):
    """Get the matching grid_ggd structure on which a GGD array is defined."""
    path = array._path
    match = re.search(r"ggd\[(\d+)\]", path)
    matching_grid_ggd = ids.grid_ggd[int(match.group(1))]
    return matching_grid_ggd


def recursive_label_search(ggd, label_list):
    """Recursively searches through a GGD structure for quantities which
    have the metadata name 'label', and appends these to the given label_list."""
    for node in ggd:
        if node.metadata.name == "label":
            label_list.append(node)
        if (
            node.metadata.data_type == IDSDataType.STRUCTURE
            or node.metadata.data_type == IDSDataType.STRUCT_ARRAY
        ):
            recursive_label_search(
                node,
                label_list,
            )


def get_filled_ggd_arrays(ids):
    """Get a list of each filled scalar and vector GGD array in the IDS."""
    ggd_list = get_ggd_aos(ids)
    scalar_arrays = []
    vector_arrays = []
    for ggd_aos in ggd_list:
        for ggd in ggd_aos:

            recursive_ggd_path_search(
                ggd._obj,
                scalar_arrays,
                vector_arrays,
            )

    return scalar_arrays, vector_arrays


# Grid rules
@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_ggd_identifier(ids):
    """Validate that the identifiers of all grid_ggds are filled."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        assert_identifier_filled(grid_ggd.identifier)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_ggd_length(ids):
    """Validate that the number of structures in the grid_ggd AoS match
    the number of time steps."""
    assert_homogeneous_time_mode(ids)
    assert len(ids.grid_ggd) == len(ids.time)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_ggd_time_homogeneous(ids):
    """Validate that there if the IDS has homogeneous time,
    the time nodes in the individual grid_ggd structures are not filled."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        assert not grid_ggd.time.has_value


# Space rules
@multi_validator(SUPPORTED_IDS_NAMES)
def validate_space_identifier(ids):
    """Validate that the identifiers of all grid_ggd spaces are filled"""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            assert_identifier_filled(space.identifier)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_space_coordinates_type_identifier(ids):
    """Validate that the space.coordinate_types match with ones that
    are in the coordinate identifier reference list."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            for coord_type in space.coordinates_type:
                assert is_index_in_identifier_ref(
                    coord_type, identifiers.coordinate_identifier
                )


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_space_geometry_type_identifier(ids):
    """Validate that the geometry_type of all spaces is at least 0
    (0 standard, 1 fourier, >1 fourier with periodicity)"""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            assert space.geometry_type.index >= 0


# Objects_per_dimension rules
@multi_validator(SUPPORTED_IDS_NAMES)
def validate_obj_per_dim_geometry_content(ids):
    """Validate that if the geometry_content is filled, its values match
    the reference ggd_geometry_content_identifier."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            for dim, obj_per_dim in enumerate(space.objects_per_dimension):
                geometry_content = obj_per_dim.geometry_content
                if geometry_content.has_value and geometry_content != 0:
                    if dim == 0:
                        assert geometry_content in {1, 11}
                    elif dim == 1:
                        assert geometry_content == 21
                    elif dim == 2:
                        assert geometry_content in {31, 32}
                    else:
                        assert False, (
                            "geometry_content undefined for "
                            "n-dimensional objects with n > 2"
                        )


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_obj_per_dim_geometry_length(ids):
    """Validate that the geometry of the objects have the correct length, according to
    its geometry_content."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            for dim, obj_per_dim in enumerate(space.objects_per_dimension):
                geometry_content = obj_per_dim.geometry_content
                for obj in obj_per_dim.object:
                    geometry = obj.geometry
                    if geometry_content.has_value and geometry_content != 0:
                        if geometry_content == 1:
                            # only contains the node coordinates
                            assert len(geometry) == len(space.coordinates_type)
                        elif geometry_content == 11:
                            # contains the node coordinates, connection length and
                            # distance in poloidal plane
                            assert len(geometry) == len(space.coordinates_type) + 2
                        elif geometry_content == 21:
                            # contains 3 surface areas
                            assert len(geometry) == 3
                        elif geometry_content == 31:
                            # contains coordinate indices (ix, iy) and volume
                            # after extension
                            assert len(geometry) == 3
                        elif geometry_content == 32:
                            # contains coordinate indices (ix, iy), volume after
                            # extension, connection length, and distance
                            # in the poloidal plane
                            assert len(geometry) == 5
                    else:
                        if geometry.has_value and dim == 0:
                            assert len(geometry) == len(space.coordinates_type)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_obj_0D_geometry_length(ids):
    """Validate that the geometry of 0D objects is larger than zero."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            obj_0D = space.objects_per_dimension[0]
            for obj in obj_0D.object:
                assert len(obj.geometry) > 0


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_obj_per_dim_nodes_length(ids):
    """Validate that the nodes of the objects have the correct length.
    0D objects should be empty or contain themselves, edges should contain 2
    nodes, while n-order should contain at least n+1 nodes."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            for dim, obj_per_dim in enumerate(space.objects_per_dimension):
                for i, obj in enumerate(obj_per_dim.object):
                    nodes = obj.nodes
                    if dim == 0:
                        if nodes.has_value:
                            assert nodes == [i + 1]
                    elif dim == 1:
                        assert len(nodes) == 2
                    else:
                        assert len(nodes) >= dim + 1


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_obj_per_dim_nodes(ids):
    """Validate that the filled nodes of an object point to
    existing nodes in the grid."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            len_0D_obj = len(space.objects_per_dimension[0].object)
            for obj_per_dim in space.objects_per_dimension:
                for obj in obj_per_dim.object:
                    if obj.nodes.has_value:
                        for node in obj.nodes:
                            assert node <= len_0D_obj


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_obj_per_dim_measure_empty(ids):
    """Validate that the measure value of 0D objects is empty."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            obj_0D = space.objects_per_dimension[0]
            for obj in obj_0D.object:
                assert not obj.measure.has_value


# Grid subset rules
@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_subset_identifier(ids):
    """Validate that grid subset identifier is filled."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            assert_identifier_filled(grid_subset.identifier)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_subset_length(ids):
    """Validate that the grid has at least 1 grid subset."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        assert len(grid_ggd.grid_subset) > 0


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_subset_space_index(ids):
    """Validate that the space in the subset points to an existing space in the grid."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    space_idx = object.space
                    assert_index_in_aos_identifier(grid_ggd.space, space_idx)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_subset_dimension_index(ids):
    """Validate that the dimension in the grid subset points to
    an existing dimension in the grid."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    dim = object.dimension
                    space_idx = object.space
                    space = find_structure_by_index(grid_ggd.space, space_idx)
                    assert len(space.objects_per_dimension) >= dim


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_subset_object_index(ids):
    """Validate that the object index in the grid subset points to an existing
    object in the grid."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    dim = object.dimension
                    space_idx = object.space
                    obj_idx = object.index
                    space = find_structure_by_index(grid_ggd.space, space_idx)
                    assert (
                        len(space.objects_per_dimension[dim._obj - 1].object) >= obj_idx
                    )


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_grid_subset_obj_dimension(ids):
    """Validate that the dimensions of the objects of which a grid subset is composed
    are not larger than the dimension of the grid subset itself."""
    assert_homogeneous_time_mode(ids)
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            subset_dim = grid_subset.dimension
            for element in grid_subset.element:
                for object in element.object:
                    obj_dim = object.dimension
                    assert subset_dim >= obj_dim


# GGD rules
@multi_validator(SUPPORTED_IDS_NAMES)
def validate_ggd_length(ids):
    """Validate that the dimensions of the GGD AoS
    matches the number of time steps."""
    assert_homogeneous_time_mode(ids)
    ggd_list = get_ggd_aos(ids)
    for ggd_aos in ggd_list:
        assert len(ggd_aos) == len(ids.time)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_ggd_time_homogeneous(ids):
    """Validate that if the IDS has homogeneous time,
    the time nodes of the individual GGD structures are not filled."""
    assert_homogeneous_time_mode(ids)
    ggd_list = get_ggd_aos(ids)
    for ggd_aos in ggd_list:
        for ggd in ggd_aos:
            assert not ggd.time.has_value


# GGD array rules
@multi_validator(SUPPORTED_IDS_NAMES)
def validate_ggd_array_match_element(ids):
    """Validate that the number of values in a GGD array match the number of elements
    in the corresponding subset. If the subset contains all nodes by
    definition, which occurs for the ggd subsets named 'nodes', 'edges', 'cells' and
    'volumes' in the reference identifier, the elements can be left empty.
    """
    assert_homogeneous_time_mode(ids)
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            grid_subset_index = sub_array.grid_subset_index
            matching_grid_ggd = get_matching_grid_ggd(ids, array)
            grid_subset = find_structure_by_index(
                matching_grid_ggd.grid_subset, grid_subset_index
            )
            if grid_subset is None:
                raise ValueError(
                    f"Could not find a grid_index with index {grid_subset_index}"
                )
            # The identifiers corresponding to nodes (1), edges (2), cells (5),
            # and volumes (43), contain all nodes by definition. Therefore,
            # the elements corresponding to these grid subsets may be left empty.
            if grid_subset.identifier.index not in [1, 2, 5, 43]:
                for quantity in sub_array:
                    if (
                        quantity.has_value
                        and quantity.metadata.name != "grid_index"
                        and quantity.metadata.name != "grid_subset_index"
                    ):
                        assert len(grid_subset.element) == len(quantity)


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_ggd_array_filled_indices(ids):
    """Validate that all GGD arrays have filled grid_index and grid_subset_index."""
    assert_homogeneous_time_mode(ids)
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            assert sub_array.grid_index.has_value
            assert sub_array.grid_subset_index.has_value


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_ggd_array_valid_grid_index(ids):
    """Validate that for the grid_index of a GGD array, the
    identifier index of the corresponding grid_ggd matches.
    """
    assert_homogeneous_time_mode(ids)
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            grid_index = sub_array.grid_index
            matching_grid_ggd = get_matching_grid_ggd(ids, sub_array)
            grid_ggd_index = matching_grid_ggd.identifier.index
            assert grid_index == grid_ggd_index


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_ggd_array_valid_grid_subset_index(ids):
    """Validate that the grid_subset_index of a GGD array matches
    with the identifier index of a grid subset.
    """
    assert_homogeneous_time_mode(ids)
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            grid_subset_index = sub_array.grid_subset_index
            matching_grid_ggd = get_matching_grid_ggd(ids, array)
            assert_index_in_aos_identifier(
                matching_grid_ggd.grid_subset, grid_subset_index
            )


@multi_validator(SUPPORTED_IDS_NAMES)
def validate_ggd_array_labels_filled(ids):
    """Validate that the labels of ions/neutrals are filled."""
    assert_homogeneous_time_mode(ids)
    ggd_list = get_ggd_aos(ids)
    label_list = []
    for ggd_aos in ggd_list:
        for ggd in ggd_aos:
            recursive_label_search(ggd._obj, label_list)
    for label in label_list:
        assert label.has_value
