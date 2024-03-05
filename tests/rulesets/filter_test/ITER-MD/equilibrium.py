@validator("equilibrium")  # noqa: F821
def equilibrium_1(eq):
    assert eq.ids_properties.homogeneous_time == 1


@validator("equilibrium")  # noqa: F821
def equilibrium_2(eq):
    assert eq.ids_properties.homogeneous_time == 1


@validator("equilibrium")  # noqa: F821
def test_3(eq):
    assert eq.ids_properties.homogeneous_time == 1


@validator("equilibrium")  # noqa: F821
def test_4(eq):
    assert eq.ids_properties.homogeneous_time == 1
