@validator("equilibrium")  # noqa: F821
def val_equilibrium_1(eq):
    assert eq.ids_properties.homogeneous_time == 1


@validator("equilibrium")  # noqa: F821
def val_equilibrium_2(eq):
    assert eq.ids_properties.homogeneous_time == 1


@validator("equilibrium")  # noqa: F821
def test_3(eq):
    assert eq.ids_properties.homogeneous_time == 1


@validator("equilibrium")  # noqa: F821
def test_4(eq):
    assert eq.ids_properties.homogeneous_time == 1
