# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("edge_profiles")
def validate_has_value(ids):
   """Validate if the property exists by using has_value method in IMASPy."""

   msg = f"must not be non empty."

   #time
   assert ids.time.has_value, msg

   #vacuum_toroidal_field
   assert ids.vacuum_toroidal_field.r0.has_value, msg
   assert ids.vacuum_toroidal_field.b0.has_value, msg

   #output_flag
   #assert ids.output_flag.has_value, msg

   #ggd
   assert ids.ggd.has_value, msg
   for itime in range(len(ids.ggd)):

      assert ids.ggd[itime].time.has_value, msg

      assert ids.ggd[itime].electrons.temperature.has_value, msg
      for i1 in range(len(ids.ggd[itime].electrons.temperature)):

         assert ids.ggd[itime].electrons.temperature[i1].values.has_value, msg

      assert ids.ggd[itime].electrons.velocity.has_value, msg

      assert ids.ggd[itime].phi_potential.has_value, msg
      for i1 in range(len(ids.ggd[itime].phi_potential)):
         assert ids.ggd[itime].phi_potential[i1].values.has_value, msg

      #ggd[:].ion
      assert ids.ggd[itime].ion.has_value, msg
      for i1 in range(len(ids.ggd)):

         assert ids.ggd[itime].ion[i1].element.has_value, msg
         for i2 in range(len(ids.ggd[itime].ion[i1].element)):

            assert ids.ggd[itime].ion[i1].element[i2].a.has_value, msg
            assert ids.ggd[itime].ion[i1].element[i2].z_n.has_value, msg
            assert ids.ggd[itime].ion[i1].element[i2].atoms_n.has_value, msg

         assert ids.ggd[itime].ion[i1].multiple_states_flag.has_value, msg

         assert ids.ggd[itime].ion[i1].state.has_value, msg
         for i2 in range(len(ids.ggd[itime].ion[i1].state)):

            assert ids.ggd[itime].ion[i1].state[i2].z_min.has_value, msg

            assert ids.ggd[itime].ion[i1].state[i2].z_max.has_value, msg
            for i3 in range(len(ids.ggd[itime].ion[i1].state[i2].density)):

               assert ids.ggd[itime].ion[i1].state[i2].density[i3].values.has_value, msg

            assert ids.ggd[itime].ion[i1].state[i2].velocity.has_value, msg

      #ggd[:].neutral
      assert ids.ggd[itime].neutral.has_value, msg
      for i1 in range(len(ids.ggd[itime].neutral)):

         assert ids.ggd[itime].neutral[i1].ion_index.has_value, msg

         assert ids.ggd[itime].neutral[i1].element.has_value, msg
         for i2 in range(len(ids.ggd[itime].neutral[i1].element)):

            assert ids.ggd[itime].neutral[i1].element[i2].a.has_value, msg
            assert ids.ggd[itime].neutral[i1].element[i2].z_n.has_value, msg
            assert ids.ggd[itime].neutral[i1].element[i2].atoms_n.has_value, msg

         assert ids.ggd[itime].neutral[i1].multiple_states_flag.has_value, msg

         assert ids.ggd[itime].neutral[i1].density.has_value, msg
         for i2 in range(len(ids.ggd[itime].neutral[i1].density)):

            assert ids.ggd[itime].neutral[i1].density[i2].values.has_value, msg

         assert ids.ggd[itime].neutral[i1].state.has_value, msg
         for i2 in range(len(ids.ggd[itime].neutral[i1].state)):

            assert ids.ggd[itime].neutral[i1].state[i2].neutral_type.name.has_value, msg

            assert ids.ggd[itime].neutral[i1].state[i2].density.has_value, msg
            for i3 in range(len(ids.ggd[itime].neutral[i1].state[i2].density)):

               assert ids.ggd[itime].neutral[i1].state[i2].density[i3].values.has_value, msg

            # path of neutral velocity is ambiguous in the ref
            assert ids.ggd[itime].neutral[i1].state[i2].velocity.has_value, msg


@validator("edge_profiles")
def validate_vacuum_toroidal_field_b0(ids):
   """Validate that vacuum_toroidal_field/b0(:) is b0 < 0."""
   for i in range(len(ids.vacuum_toroidal_field.b0)):
      b0 = ids.vacuum_toroidal_field.b0[i]
      assert b0 < 0., f"vacuum_toroidal_field.b0[{i}]={b0} is not in range of b0 < 0."
