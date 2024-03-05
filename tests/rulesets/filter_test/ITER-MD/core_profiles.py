@validator("core_profiles")  # noqa: F821
def core_profiles_1(cp):
    assert cp.ids_properties.homogeneous_time == 1


@validator("core_profiles")  # noqa: F821
def core_profiles_2(cp):
    assert cp.ids_properties.homogeneous_time == 1


@validator("core_profiles")  # noqa: F821
def test_3(cp):
    assert cp.ids_properties.homogeneous_time == 1


@validator("core_profiles")  # noqa: F821
def test_4(cp):
    assert cp.ids_properties.homogeneous_time == 1
