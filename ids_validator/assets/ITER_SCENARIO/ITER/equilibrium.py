# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("equilibrium")
def validate_has_value(ids):
   """Validate if the property exists by using has_value method in IMASPy."""

   msg = f"must not be non empty."
      
   #time_slice[:]
   assert ids.time_slice.has_value, msg
   for itime in range(len(ids.time_slice)):

      #time_slice[:].global_quantities.ip
      assert ids.time_slice[itime].global_quantities.ip.has_value, msg

      #time_slice[:].profiles_2d[:]
      assert ids.time_slice[itime].profiles_2d.has_value, msg
      for i1 in range(len(ids.time_slice[itime].profiles_2d)):

         assert ids.time_slice[itime].profiles_2d[i1].phi.has_value, msg
         assert ids.time_slice[itime].profiles_2d[i1].psi.has_value, msg
         assert ids.time_slice[itime].profiles_2d[i1].r.has_value, msg
         assert ids.time_slice[itime].profiles_2d[i1].z.has_value, msg

   #vacuum_toroidal_field.r0
   assert ids.vacuum_toroidal_field.r0.has_value, msg

   #vacuum_toroidal_field.b0[:]
   assert ids.vacuum_toroidal_field.b0.has_value, msg


@validator("equilibrium")
def validate_global_quantities_ip(ids):
   """Validate that time_slice(:)/global_quantities/ip is in range of -17MA < ip <= 0."""
   for itime, time_slice in enumerate(ids.time_slice):
      ip = time_slice.global_quantities.ip
      assert -17000000. < ip <= 0., f"time_slice[{itime}].global_quantities.ip={ip} is not in range of -17MA < ip <= 0" 
      #assert ip > 0., f"time_slice[{i}].global_quantities.ip={ip} is not in range of -17MA < ip <= 0" 


@validator("equilibrium")
def validate_vacuum_toroidal_field_b0(ids):
   """Validate that vacuum_toroidal_field/b0(:) is b0 < 0."""
   for i in range(len(ids.vacuum_toroidal_field.b0)):
      b0 = ids.vacuum_toroidal_field.b0[i]
      assert b0 < 0., f"vacuum_toroidal_field.b0[{i}]={b0} is not in range of b0 < 0."
