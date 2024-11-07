"""Rules applying to all IDSs containing GGDs"""
from imaspy.ids_defs import IDS_TIME_MODE_HOMOGENEOUS
from imaspy import identifiers

SUPPORTED_IDS_NAMES = (
    "edge_profiles",
    "edge_sources",
    "edge_transport",
    "mhd",
    "radiation",
    "runaway_electrons",
    "wall",
)

EXPERIMENTAL_IDS_NAMES = [
    "equilibrium",
    "distribution_sources",
    "distributions",
    "tf",
    "transport_solver_numerics",
    "waves",
]

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
                assert is_index_in_identifiers(coord_type, identifiers.coordinate_identifier)

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
                        assert False, "Geometry content undefined for n-dimensional objects with n>2"

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
                        assert len(geometry) == len(space.coordinates_type)
