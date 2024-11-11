"""Rules applying to all IDSs containing GGDs"""

import re
from os import walk

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

#   EXPERIMENTAL_IDS_NAMES = [
#       "equilibrium",
#       "distribution_sources",
#       "distributions",
#       "tf",
#       "transport_solver_numerics",
#       "waves",
#   ]


def validate_identifier(identifier):
    """Validate that an identifier has its name, index and description filled"""
    assert identifier.name.has_value
    assert identifier.index.has_value
    assert identifier.description.has_value


def is_index_in_identifiers(index, identifier_list):
    """Checks if an index appears in an identifier list"""
    return any(index == member.value for member in identifier_list)


# TODO: only test on GGD IDS instead of all


# Grid rules
@validator("*")
def validate_grid_ggd_identifier(ids):
    """Validate that the identifiers of all grid_ggds are filled"""
    for grid_ggd in ids.grid_ggd:
        validate_identifier(grid_ggd.identifier)


@validator("*")
def validate_grid_ggd_length(ids):
    """Validate that there are as many grids as there are time steps"""
    assert len(ids.grid_ggd) == len(ids.time)


@validator("*")
def validate_grid_ggd_time_homogeneous(ids):
    """Validate that there if the IDS has homogeneous time, the individual grid_ggd time nodes are not filled."""
    if ids.ids_properties.homogeneous_time == IDS_TIME_MODE_HOMOGENEOUS:
        for grid_ggd in ids.grid_ggd:
            assert not grid_ggd.time.has_value


# Space rules
@validator("*")
def validate_space_identifier(ids):
    """Validate that the identifiers of all grid_ggd spaces are filled"""
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            validate_identifier(space.identifier)


@validator("*")
def validate_space_coordinates_type_identifier(ids):
    """Validate that the coordinate type identifiers match"""
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            for coord_type in space.coordinates_type:
                assert is_index_in_identifiers(
                    coord_type, identifiers.coordinate_identifier
                )


@validator("*")
def validate_space_geometry_type_identifier(ids):
    """Validate that the geometry_type is at least 0
    (0 standard, 1 fourier, >1 fourier with periodicity)"""
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            assert space.geometry_type.index >= 0


# Objects_per_dimension rules
@validator("*")
def validate_obj_per_dim_geometry_content(ids):
    """Validate that the geometry_content match the ggd_geometry_content_identifier"""
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
                        assert (
                            False
                        ), "Geometry content undefined for n-dimensional objects with n>2"


@validator("*")
def validate_obj_per_dim_geometry_length(ids):
    """Validate that the geometry of the objects have the correct length, according to
    its geometry_content"""
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            for obj_per_dim in space.objects_per_dimension:
                geometry_content = obj_per_dim.geometry_content
                for obj in obj_per_dim.object:
                    geometry = obj.geometry
                    if geometry_content.has_value and geometry_content != 0:
                        if geometry_content == 1:
                            assert len(geometry) == len(space.coordinates_type)
                        elif geometry_content == 11:
                            assert len(geometry) == len(space.coordinates_type) + 2
                        elif geometry_content == 21:
                            assert len(geometry) == 3
                        elif geometry_content == 31:
                            assert len(geometry) == 3
                        elif geometry_content == 32:
                            assert len(geometry) == 5
                    else:
                        if geometry.has_value:
                            assert len(geometry) == len(space.coordinates_type)


@validator("*")
def validate_obj_0D_geometry_length(ids):
    """Validate that the geometry of 0D objects is larger than zero."""
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            obj_0D = space.objects_per_dimension[0]
            for obj in obj_0D.object:
                assert len(obj.geometry) > 0


@validator("*")
def validate_obj_per_dim_nodes_length(ids):
    """Validate that the nodes of the objects have the correct length.
    0D objects should be empty or contain themselves, edges should contain 2
    nodes, while n-order should contain at least n+1 nodes."""
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


@validator("*")
def validate_obj_per_dim_nodes(ids):
    """Validate that the filled object nodes point to existing nodes in the grid."""
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            len_0D_obj = len(space.objects_per_dimension[0].object)
            for obj_per_dim in space.objects_per_dimension:
                for obj in obj_per_dim.object:
                    if obj.nodes.has_value:
                        for node in obj.nodes:
                            assert node <= len_0D_obj


@validator("*")
def validate_obj_per_dim_measure_empty(ids):
    """Validate that the measure value of 0D objects is empty."""
    for grid_ggd in ids.grid_ggd:
        for space in grid_ggd.space:
            obj_0D = space.objects_per_dimension[0]
            for obj in obj_0D.object:
                assert not obj.measure.has_value


# Grid subset rules
@validator("*")
def validate_grid_subset_identifier(ids):
    """Validate the grid subset identifier."""
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            validate_identifier(grid_subset.identifier)


@validator("*")
def validate_grid_subset_length(ids):
    """Validate that the grid has at least 1 grid subset."""
    for grid_ggd in ids.grid_ggd:
        assert len(grid_ggd.grid_subset) > 0


def is_index_in_aos_identifier(aos, index):
    """Check if an index appears exactly once in the identifier of an AoS."""
    matches = sum(1 for structure in aos if structure.identifier.index == index)
    assert matches == 1


def find_index_match_in_aos_identifier(aos, index):
    """Return the first object in 'aos' whose identifier.index matches the given index, or None if no match is found."""
    for structure in aos:
        if structure.identifier.index == index:
            return structure


@validator("*")
def validate_grid_subset_space_index(ids):
    """Validate that the space in the subset points to an existing space in the grid."""
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    space_idx = object.space
                    is_index_in_aos_identifier(grid_ggd.space, space_idx)


@validator("*")
def validate_grid_subset_dimension_index(ids):
    """Validate that the dimension in the subset points to an existing dimension in the grid."""
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    dim = object.dimension
                    space_idx = object.space
                    space = find_index_match_in_aos_identifier(
                        grid_ggd.space, space_idx
                    )
                    assert len(space.objects_per_dimension) >= dim


@validator("*")
def validate_grid_subset_object_index(ids):
    """Validate that the object index in the subset points to an existing object in the grid."""
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    dim = object.dimension
                    space_idx = object.space
                    obj_idx = object.index
                    space = find_index_match_in_aos_identifier(
                        grid_ggd.space, space_idx
                    )
                    assert (
                        len(space.objects_per_dimension[dim._obj - 1].object) >= obj_idx
                    )


@validator("*")
def validate_grid_subset_obj_dimension(ids):
    """Validate that the dimensions of the object are not larger than the object of the grid subset."""
    for grid_ggd in ids.grid_ggd:
        for grid_subset in grid_ggd.grid_subset:
            subset_dim = grid_subset.dimension
            for element in grid_subset.element:
                for object in element.object:
                    obj_dim = object.dimension
                    assert subset_dim >= obj_dim


# GGD rules


def get_ggd(ids):
    """Get all GGD base nodes"""
    ggd_list = []
    for node in Select(ids, "(^|/)ggd$", leaf_only=False):
        if node.metadata.name == "ggd":
            parent_node = imaspy.util.get_parent(node._obj)
            if parent_node.metadata.name != "ggd":
                ggd_list.append(node)
    return ggd_list


@validator("*")
def validate_ggd_length(ids):
    """Validate that the dimensions of the GGD match the number of time steps."""
    ggd_list = get_ggd(ids)
    for ggd_aos in ggd_list:
        assert len(ggd_aos) == len(ids.time)


@validator("*")
def validate_ggd_time_homogeneous(ids):
    """Validate that there if the IDS has homogeneous time, the individual ggd time nodes are not filled."""
    ggd_list = get_ggd(ids)
    if ids.ids_properties.homogeneous_time == IDS_TIME_MODE_HOMOGENEOUS:
        for ggd_aos in ggd_list:
            for ggd in ggd_aos:
                assert not ggd.time.has_value


# GGD array rules
def get_filled_ggd_arrays(ids):
    ggd_list = get_ggd(ids)
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


def recursive_ggd_path_search(quantity, scalar_array, vector_array):
    """Recursively searches through the metadata of an IDS node for scalar GGD arrays
    (real & complex) and vector GGD arrays (regular and rphiz), and appends the paths of
    these to the scalar_array_paths and vector_array_paths respectively.

    Args:
        quantity_metadata: The metadata of an IDS node
        scalar_array_paths: The IDSPaths of GGD scalar arrays (real & complex)
        vector_array_paths: The IDSPaths of GGD vector arrays (regular and rphiz)
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
                scalar_array.append(subquantity)

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
                vector_array.append(subquantity)

        if subquantity.metadata.data_type == IDSDataType.STRUCTURE:
            recursive_ggd_path_search(
                subquantity,
                scalar_array,
                vector_array,
            )


@validator("edge_profiles")
def validate_ggd_array_match_element(ids):
    return
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            grid_subset_index = sub_array.grid_subset_index
            matching_grid_ggd = get_matching_grid_ggd(ids, array)
            grid_subset = find_index_match_in_aos_identifier(
                matching_grid_ggd.grid_subset, grid_subset_index
            )
            if grid_subset is None:
                return
            if not grid_subset.identifier.index in [1, 2, 5, 43]:
                for quantity in sub_array:
                    if (
                        quantity.has_value
                        and quantity.metadata.name != "grid_index"
                        and quantity.metadata.name != "grid_subset_index"
                    ):
                        assert len(grid_subset.element) == len(quantity)


@validator("*")
def validate_ggd_array_filled_indices(ids):
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            assert sub_array.grid_index.has_value
            assert sub_array.grid_subset_index.has_value


def get_matching_grid_ggd(ids, array):
    path = array._path
    match = re.search(r"ggd\[(\d+)\]", path)
    matching_grid_ggd = ids.grid_ggd[int(match.group(1))]
    return matching_grid_ggd


@validator("*")
def validate_ggd_array_valid_grid_index(ids):
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            grid_index = sub_array.grid_index
            matching_grid_ggd = get_matching_grid_ggd(ids, sub_array)
            grid_ggd_index = matching_grid_ggd.identifier.index
            assert grid_index == grid_ggd_index


@validator("*")
def validate_ggd_array_valid_grid_subset_index(ids):
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)
    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            grid_subset_index = sub_array.grid_subset_index
            matching_grid_ggd = get_matching_grid_ggd(ids, array)
            is_index_in_aos_identifier(matching_grid_ggd.grid_subset, grid_subset_index)


def recursive_label_search(ggd, label_list):
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


@validator("*")
def validate_ggd_array_labels_filled(ids):
    """Validate that the labels of ions/neutrals are filled."""
    ggd_list = get_ggd(ids)
    label_list = []
    for ggd_aos in ggd_list:
        for ggd in ggd_aos:
            recursive_label_search(ggd._obj, label_list)
    for label in label_list:
        assert label.has_value
