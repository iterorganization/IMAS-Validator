#

@validator("equilibrium")
def validate_global_quantities_ip(ids):
   """Validate that time_slice(:)/global_quantities/ip is in range of -17MA < ip <= 0."""
   for i, time_slice in enumerate(ids.time_slice):
      ip = time_slice.global_quantities.ip
      assert -17000000. < ip <= 0., f"time_slice[{i}].global_quantities.ip={ip} is not in range of -17MA < ip <= 0" 

@validator("equilibrium")
def validate_vacuum_toroidal_field_b0(ids):
   """Validate that vacuum_toroidal_field/b0(:) is b0 < 0."""
   for i in range(len(ids.vacuum_toroidal_field.b0)):
      b0 = ids.vacuum_toroidal_field.b0[i]
      assert b0 < 0., f"vacuum_toroidal_field.b0[{i}]={b0} is not in range of b0 < 0."
