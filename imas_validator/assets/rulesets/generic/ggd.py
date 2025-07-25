"""Rules applying to all IDSs containing GGDs"""

from imas import identifiers
from imas.ids_data_type import IDSDataType
from imas.ids_defs import IDS_TIME_MODE_HETEROGENEOUS, IDS_TIME_MODE_HOMOGENEOUS

# As IDSs store their GGD grid and GGD AoS in different locations, they are explicitly
# mapped here. If you want to enable GGD validation for a new IDS, amend it to this
# mapping. This takes the following form:
# "<IDS name>": ("<GGD grid IDS path>", ["<GGD IDS path1>", "<GGD IDS path2>", ...])
GGD_PATHS_PER_IDS = {
    "edge_profiles": ("grid_ggd", ["ggd", "ggd_fast"]),
    "edge_sources": ("grid_ggd", ["source/ggd", "source/ggd_fast"]),
    "edge_transport": ("grid_ggd", ["model/ggd", "model/ggd_fast"]),
    "mhd": ("grid_ggd", ["ggd"]),
    "radiation": ("grid_ggd", ["process/ggd"]),
    "runaway_electrons": ("grid_ggd", ["ggd_fluid"]),
    "plasma_profiles": ("grid_ggd", ["ggd", "ggd_fast"]),
    "plasma_sources": ("grid_ggd", ["source/ggd", "source/ggd_fast"]),
    "plasma_transport": ("grid_ggd", ["model/ggd", "model/ggd_fast"]),
    "wall": ("description_ggd/grid_ggd", ["description_ggd/ggd"]),
    "equilibrium": ("grids_ggd/grid", ["time_slice/ggd"]),
    "distribution_sources": ("source/ggd/grid", ["source/ggd"]),
    "distributions": ("distribution/ggd/grid", ["distribution/ggd"]),
    "tf": ("field_map/grid", ["field_map"]),
    "transport_solver_numerics": (
        "boundary_conditions_ggd/grid",
        ["boundary_conditions_ggd"],
    ),
    "waves": ("coherent_wave/full_wave/grid", ["coherent_wave/full_wave"]),
}


# Helper functions
def has_homogeneous_time(ids):
    return ids.ids_properties.homogeneous_time == IDS_TIME_MODE_HOMOGENEOUS


def has_heterogeneous_time(ids):
    return ids.ids_properties.homogeneous_time == IDS_TIME_MODE_HETEROGENEOUS


def multi_validator(ggd_mapping):
    """Decorator to apply the @validator decorator for multiple IDSs."""

    def decorator(func):
        for name in list(ggd_mapping):
            func = validator(name)(func)
        return func

    return decorator


def assert_index_in_identifier_reference(index, identifier_ref):
    """Asserts that an index exists in the identifier reference."""
    assert any(index == member.value for member in identifier_ref), (
        f"Identifier index {index} does not appear in {identifier_ref}"
    )


def assert_valid_identifier(identifier, identifier_ref=None):
    """Asserts that an identifier has its name, index and description fields filled."""
    assert identifier.name.has_value, "Identifier name must be filled"
    assert identifier.index.has_value, "Identifier index must be filled"
    assert identifier.description.has_value, "Identifier description must be filled"
    if identifier_ref is not None:
        assert_index_in_identifier_reference(identifier.index, identifier_ref)


def assert_index_in_aos_identifier(aos, index):
    """Asserts that a given index appears exactly once in the index identifiers of
    a structure of an AoS."""
    matches = sum(1 for structure in aos if structure.identifier.index == index)
    assert matches == 1, (
        f"{aos.metadata.path} should contain exactly one element with "
        f"`identifier.index` equal to {index}, but found {matches} elements instead."
    )


def find_structure_by_index(list_of_aos, index):
    """Return the first object in a list of AoSs whose identifier.index matches the
    given index, or None if no match is found."""
    for aos in list_of_aos:
        for structure in aos:
            if structure.identifier.index == index:
                return structure
    assert False, f"{list_of_aos} does not have an AoS with identifier index of {index}"


def recursive_ggd_path_search(quantity, scalar_list, vector_list):
    """Recursively searches through an IDS node for scalar GGD arrays
    (real & complex) and vector GGD arrays (regular and rphiz), and stores
    these in the scalar and vector lists, respectively.
    """
    for subquantity in quantity.iter_nonempty_():
        if subquantity.metadata.data_type == IDSDataType.STRUCT_ARRAY:
            # Get scalar and complex scalar array quantities
            if subquantity.metadata.structure_reference in [
                "generic_grid_scalar",
                "generic_grid_scalar_complex",
            ]:
                scalar_list.append(subquantity)

            # Get vector and rzphi-vector array quantities
            # From DDv4 onward `generic_grid_vector_components_rzphi` will be
            # replaced by `generic_grid_vector_components_rphiz`
            elif subquantity.metadata.structure_reference in [
                "generic_grid_vector_components",
                "generic_grid_vector_components_rzphi",
                "generic_grid_vector_components_rphiz",
            ]:
                vector_list.append(subquantity)

        if subquantity.metadata.data_type == IDSDataType.STRUCTURE:
            recursive_ggd_path_search(
                subquantity,
                scalar_list,
                vector_list,
            )


def get_filled_ggd_arrays(ids):
    """Get a list of each filled scalar and vector GGD array in the IDS."""
    scalar_arrays = []
    vector_arrays = []
    for ggd in get_ggds(ids):
        recursive_ggd_path_search(
            ggd,
            scalar_arrays,
            vector_arrays,
        )

    return scalar_arrays, vector_arrays


def get_objects_from_path(ids, path, descend_final):
    """Returns IDS objects found by traversing an IDSPath. If descend_final is True,
    returns elements of the final AoS; otherwise, returns the AoS itself.
    """
    parts = path.split("/")

    current = [ids]
    for i, part in enumerate(parts):
        next_level = []
        for obj in current:
            # If IDS path cannot be found, skip it
            if not hasattr(obj, part):
                continue
            attr = obj[part]
            if i == len(parts) - 1 and not descend_final:
                next_level.append(attr)
            else:
                next_level.extend(attr)
        current = next_level

    return current


def get_ggds(ids, descend_final=True):
    """Get a list of all GGD nodes in the IDS"""
    _, ggd_map = GGD_PATHS_PER_IDS[str(ids.metadata.name)]
    if not ggd_map:
        return []
    ggds = []
    for ggd_path in ggd_map:
        current_ggds = get_objects_from_path(ids, ggd_path, descend_final)
        ggds.extend(current_ggds)
    return ggds


def get_grid_ggds(ids, descend_final=True):
    """Get a list of all grid GGD nodes in the IDS"""
    grid_ggd_map, _ = GGD_PATHS_PER_IDS[str(ids.metadata.name)]
    if not grid_ggd_map:
        return []
    return get_objects_from_path(ids, grid_ggd_map, descend_final)


def get_defined_grids(ids):
    """Get a list of each grid GGD that does not have a reference to other IDS."""
    non_referenced_grids = []
    for grid_ggd in get_grid_ggds(ids):
        # TODO: Referenced grids are currently not checked
        if not grid_ggd.path:
            non_referenced_grids.append(grid_ggd)
    return non_referenced_grids


# Grid rules
@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_ggd_identifier(ids):
    """Validate that the identifiers of all grid_ggds are filled."""
    for grid_ggd in get_defined_grids(ids):
        assert_valid_identifier(grid_ggd.identifier, identifiers.ggd_identifier)


@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_ggd_size(ids):
    """Validate that the number of structures in the grid_ggd AoS match
    the number of time steps if the IDS has homogeneous time."""
    if has_homogeneous_time(ids):
        grid_ggds = get_grid_ggds(ids, descend_final=False)
        for grid_ggd in grid_ggds:
            if grid_ggd.metadata.structure_reference == "generic_grid_aos3_root":
                assert len(grid_ggd) == len(ids.time), (
                    "Number of grid_ggd structures must match the number of time steps"
                )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_ggd_time(ids):
    """Validate that if the IDS has heterogeneous time,
    the time nodes in the individual grid_ggd structures are filled."""
    if has_heterogeneous_time(ids):
        for grid_ggd in get_defined_grids(ids):
            assert grid_ggd.time.has_value, (
                "Time nodes in individual grid_ggd structures should be filled "
                "for heterogeneous time"
            )


# Space rules
@multi_validator(GGD_PATHS_PER_IDS)
def validate_space_identifier(ids):
    """Validate that the identifiers of all grid_ggd spaces are filled"""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            assert_valid_identifier(space.identifier, identifiers.ggd_space_identifier)


@multi_validator(GGD_PATHS_PER_IDS)
def validate_space_coordinates_type_identifier(ids):
    """Validate that the space.coordinate_types match with ones that
    are in the coordinate identifier reference list."""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            coordinates_type = space.coordinates_type
            # in DDv3 coordinates_type was a INT_1D, since DDv4 it's an AoS of
            # coordinate_identifiers
            if coordinates_type.metadata.data_type == IDSDataType.INT:
                for coord_type in coordinates_type:
                    assert_index_in_identifier_reference(
                        coord_type, identifiers.coordinate_identifier
                    )
            else:
                for coord_type_identifier in coordinates_type:
                    assert_valid_identifier(
                        coord_type_identifier, identifiers.coordinate_identifier
                    )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_space_geometry_type_identifier(ids):
    """Validate that the geometry_type of all spaces is at least 0
    (0 standard, 1 fourier, >1 fourier with periodicity)"""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            assert space.geometry_type.index >= 0, (
                "space.geometry_type.index must be >= 0"
            )


# Objects_per_dimension rules
@multi_validator(GGD_PATHS_PER_IDS)
def validate_obj_per_dim_geometry_content(ids):
    """Validate that if the geometry_content is filled, its values match
    the reference ggd_geometry_content_identifier."""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            for dim, obj_per_dim in enumerate(space.objects_per_dimension):
                geometry_content = obj_per_dim.geometry_content.index
                if geometry_content.has_value and geometry_content != 0:
                    # When the geometry content is filled, they should adhere to
                    # the indices provided in the ggd_geometry_content_identifier.
                    # These determine what information is stored in the geometry nodes.
                    # What each of these geometry content indices mean, is described in
                    # more detail in validate_obj_per_dim_geometry_length()
                    if dim == 0:
                        assert int(geometry_content) in {1, 11}, (
                            "0D geometry_content must be either 1, or 11"
                        )
                    elif dim == 1:
                        assert int(geometry_content) == 21, (
                            "1D geometry_content must be 21"
                        )
                    elif dim == 2:
                        assert int(geometry_content) in {31, 32}, (
                            "2D geometry_content must be either 31, or 32"
                        )
                    else:
                        assert False, (
                            "geometry_content undefined for "
                            "n-dimensional objects with n > 2"
                        )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_obj_per_dim_geometry_size(ids):
    """Validate that the geometry of the objects have the correct length, according to
    its geometry_content."""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            for dim, obj_per_dim in enumerate(space.objects_per_dimension):
                geometry_content = obj_per_dim.geometry_content
                for obj in obj_per_dim.object:
                    geometry = obj.geometry
                    if geometry_content.has_value and geometry_content != 0:
                        if geometry_content == 1:
                            # only contains the node coordinates
                            assert len(geometry) == len(space.coordinates_type), (
                                "geometry length must be equal to number of "
                                "coordinate types for node_coordinates"
                            )
                        elif geometry_content == 11:
                            # contains the node coordinates, connection length and
                            # distance in poloidal plane
                            assert len(geometry) == len(space.coordinates_type) + 2, (
                                "geometry length must be equal to number of "
                                "coordinate types + 2 for node_coordinates_connection"
                            )
                        elif geometry_content == 21:
                            # contains 3 surface areas
                            assert len(geometry) == 3, (
                                "geometry length must be 3 for edge_areas"
                            )
                        elif geometry_content == 31:
                            # contains coordinate indices (ix, iy) and volume
                            # after extension
                            assert len(geometry) == 3, (
                                "geometry length must be 3 for face_indices_volume"
                            )
                        elif geometry_content == 32:
                            # contains coordinate indices (ix, iy), volume after
                            # extension, connection length, and distance
                            # in the poloidal plane
                            assert len(geometry) == 5, (
                                "geometry length must be 5 for "
                                "face_indices_volume_connection"
                            )
                    else:
                        if geometry.has_value and dim == 0:
                            assert len(geometry) == len(space.coordinates_type), (
                                "geometry length must be equal to number of "
                                "coordinate types"
                            )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_obj_0D_geometry_size(ids):
    """Validate that the geometry of 0D objects is larger than zero."""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            obj_0D = space.objects_per_dimension[0]
            for obj in obj_0D.object:
                assert len(obj.geometry) > 0, (
                    "length of geometry of 0D objects must be > 0"
                )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_obj_per_dim_nodes_size(ids):
    """Validate that the nodes of the objects have the correct length.
    0D objects should be empty or contain themselves, edges should contain 2
    nodes, while n-order should contain at least n+1 nodes."""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            for dim, obj_per_dim in enumerate(space.objects_per_dimension):
                for i, obj in enumerate(obj_per_dim.object):
                    nodes = obj.nodes
                    if dim == 0:
                        if nodes.has_value:
                            assert nodes == [i + 1], (
                                "nodes of 0D objects should be empty or "
                                "contain themselves"
                            )
                    elif dim == 1:
                        assert len(nodes) == 2, "edges must contain 2 nodes"
                    else:
                        assert len(nodes) >= dim + 1, (
                            "n-order objects must contain at least n+1 nodes"
                        )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_obj_per_dim_nodes(ids):
    """Validate that the filled nodes of an object point to
    existing nodes in the grid."""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            len_0D_obj = len(space.objects_per_dimension[0].object)
            for obj_per_dim in space.objects_per_dimension:
                for obj in obj_per_dim.object:
                    if obj.nodes.has_value:
                        assert (0 < obj.nodes).all(), "object nodes must be positive"
                        assert (obj.nodes <= len_0D_obj).all(), (
                            "object nodes must point to existing nodes"
                        )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_obj_per_dim_measure_empty(ids):
    """Validate that the measure value of 0D objects is empty or zero."""
    for grid_ggd in get_defined_grids(ids):
        for space in grid_ggd.space:
            obj_0D = space.objects_per_dimension[0]
            for obj in obj_0D.object:
                assert not obj.measure.has_value or obj.measure.value == 0, (
                    "measure of 0D objects must be empty or zero"
                )


# Grid subset rules
@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_subset_identifier(ids):
    """Validate that grid subset identifier is filled."""
    for grid_ggd in get_defined_grids(ids):
        for grid_subset in grid_ggd.grid_subset:
            assert_valid_identifier(
                grid_subset.identifier, identifiers.ggd_subset_identifier
            )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_subset_size(ids):
    """Validate that the grid has at least 1 grid subset."""
    for grid_ggd in get_defined_grids(ids):
        assert len(grid_ggd.grid_subset) > 0, (
            "GGD grid must have at least 1 grid_subset"
        )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_subset_space_index(ids):
    """Validate that the space in the subset points to an existing space in the grid."""
    for grid_ggd in get_defined_grids(ids):
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    space_idx = object.space
                    assert_index_in_aos_identifier(grid_ggd.space, space_idx)


@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_subset_dimension_index(ids):
    """Validate that the dimension in the grid subset points to
    an existing dimension in the grid."""
    for grid_ggd in get_defined_grids(ids):
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    dim = object.dimension
                    space_idx = object.space
                    space = find_structure_by_index([grid_ggd.space], space_idx)
                    if space is None:
                        continue
                    assert len(space.objects_per_dimension) >= dim, (
                        "dimension in grid_subset must point to an existing dimension "
                        "in the grid"
                    )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_subset_object_index(ids):
    """Validate that the object index in the grid subset points to an existing
    object in the grid."""
    for grid_ggd in get_defined_grids(ids):
        for grid_subset in grid_ggd.grid_subset:
            for element in grid_subset.element:
                for object in element.object:
                    dim = object.dimension
                    space_idx = object.space
                    obj_idx = object.index
                    space = find_structure_by_index([grid_ggd.space], space_idx)
                    if space is None:
                        continue
                    assert (
                        len(space.objects_per_dimension[dim - 1].object) >= obj_idx > 0
                    ), "object index must point to an existing object in the grid"


@multi_validator(GGD_PATHS_PER_IDS)
def validate_grid_subset_obj_dimension(ids):
    """Validate that the dimensions of the objects of which a grid subset is composed
    are not larger than the dimension of the grid subset itself."""
    for grid_ggd in get_defined_grids(ids):
        for grid_subset in grid_ggd.grid_subset:
            subset_dim = grid_subset.dimension
            for element in grid_subset.element:
                for object in element.object:
                    obj_dim = object.dimension
                    assert subset_dim >= obj_dim, (
                        "object dimension must be smaller or equal to the dimension of the grid subset"
                    )


# GGD rules
@multi_validator(GGD_PATHS_PER_IDS)
def validate_ggd_size(ids):
    """Validate that the dimensions of the GGD AoS matches the number of time steps."""

    if has_homogeneous_time(ids):
        ggd_list = get_ggds(ids, descend_final=False)
        for ggd_aos in ggd_list:
            assert len(ggd_aos) == len(ids.time), (
                "the length of the array of structures of the GGD must "
                "match number of time steps"
            )


# GGD array rules
@multi_validator(GGD_PATHS_PER_IDS)
def validate_ggd_arrays(ids):
    """Validate that the GGD grid and grid subset referenced in GGD arrays exist.
    The number of values in a GGD array should match the number of elements
    in the corresponding subset. If the subset contains all nodes by
    definition, which occurs for the ggd subsets named 'nodes', 'edges', 'cells' and
    'volumes' in the reference identifier, the elements can be left empty.
    """
    scalar_arrays, vector_arrays = get_filled_ggd_arrays(ids)

    for array in scalar_arrays + vector_arrays:
        for sub_array in array:
            assert sub_array.grid_index.has_value, (
                "the grid_index of a GGD array must be filled"
            )
            grid_index = sub_array.grid_index

            assert sub_array.grid_subset_index.has_value, (
                "the grid_subset_index of a GGD array must be filled"
            )
            grid_subset_index = sub_array.grid_subset_index

            assert sub_array.has_value, (
                "at least one quantity of a GGD array must be filled"
            )

            matching_grid_ggd = find_structure_by_index(
                get_grid_ggds(ids, descend_final=False), grid_index
            )

            # NOTE: grids with references to another IDS are not validated
            if matching_grid_ggd is None or matching_grid_ggd.path:
                continue

            grid_subset = find_structure_by_index(
                [matching_grid_ggd.grid_subset], grid_subset_index
            )
            # For the grid subsets 'nodes', 'edges', 'cells' and 'volumes' which have
            # indices 1, 2, 5, 43 respectively, elements may be empty
            if grid_subset is None or grid_subset.identifier.index in [1, 2, 5, 43]:
                continue

            for quantity in sub_array.iter_nonempty_():
                if (
                    quantity.metadata.name != "grid_index"
                    and quantity.metadata.name != "grid_subset_index"
                ):
                    assert len(grid_subset.element) == len(quantity), (
                        "number of values in GGD array must match number of elements"
                    )


@multi_validator(GGD_PATHS_PER_IDS)
def validate_ggd_array_labels_filled(ids):
    """Validate that the labels of ions/neutrals are filled."""
    for label in Select(ids, "/label$"):
        assert label.has_value, "labels of ions/neutrals must be filled"
