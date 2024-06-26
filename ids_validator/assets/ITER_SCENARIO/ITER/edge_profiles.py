#

@validator("edge_profiles")
def validate_vacuum_toroidal_field_b0(ids):
   """Validate that vacuum_toroidal_field/b0(:) is b0 < 0."""
   for i in range(len(ids.vacuum_toroidal_field.b0)):
      b0 = ids.vacuum_toroidal_field.b0[i]
      assert b0 < 0., f"vacuum_toroidal_field.b0[{i}]={b0} is not in range of b0 < 0."
