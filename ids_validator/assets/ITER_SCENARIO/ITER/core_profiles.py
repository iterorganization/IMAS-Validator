# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("core_profiles")
def validate_has_value(ids):
   """Validate if the property exists by using has_value method in IMASPy."""

   msg = f"must not be non empty."

   #global_quantities
   assert ids.global_quantities.beta_pol.has_value, msg
   assert ids.global_quantities.beta_tor_norm.has_value, msg
   assert ids.global_quantities.current_bootstrap.has_value, msg
   assert ids.global_quantities.current_non_inductive.has_value, msg
   assert ids.global_quantities.energy_diamagnetic.has_value, msg
   assert ids.global_quantities.ip.has_value, msg
   assert ids.global_quantities.v_loop.has_value, msg

   #profiles_1d
   assert ids.profiles_1d.has_value, msg
   for itime in range(len(ids.profiles_1d)):
      assert ids.profiles_1d[itime].e_field.radial.has_value, msg
      assert ids.profiles_1d[itime].electrons.density.has_value, msg
      assert ids.profiles_1d[itime].electrons.pressure.has_value, msg
      assert ids.profiles_1d[itime].electrons.pressure_fast_parallel.has_value, msg
      assert ids.profiles_1d[itime].electrons.pressure_fast_perpendicular.has_value, msg
      assert ids.profiles_1d[itime].electrons.pressure_thermal.has_value, msg
      assert ids.profiles_1d[itime].electrons.temperature.has_value, msg
      assert ids.profiles_1d[itime].grid.rho_tor.has_value, msg
      assert ids.profiles_1d[itime].grid.rho_tor_norm.has_value, msg
      assert ids.profiles_1d[itime].grid.psi.has_value, msg
      assert ids.profiles_1d[itime].grid.volume.has_value, msg

      #profiles_1d[:].ion
      assert ids.profiles_1d[itime].ion.has_value, msg
      for i1 in range(len(ids.profiles_1d[itime].ion)):

         assert ids.profiles_1d[itime].ion[i1].density.has_value, msg

         #profiles_1d[:].ion[:].element
         assert ids.profiles_1d[itime].ion[i1].element.has_value, msg
         for i2 in range(len(ids.profiles_1d[itime].ion[i1].element)):

            assert ids.profiles_1d[itime].ion[i1].element[i2].a.has_value, msg
            assert ids.profiles_1d[itime].ion[i1].element[i2].z_n.has_value, msg

         assert ids.profiles_1d[itime].ion[i1].pressure.has_value, msg
         assert ids.profiles_1d[itime].ion[i1].pressure_fast_parallel.has_value, msg
         assert ids.profiles_1d[itime].ion[i1].pressure_fast_perpendicular.has_value, msg
         assert ids.profiles_1d[itime].ion[i1].pressure_thermal.has_value, msg
         assert ids.profiles_1d[itime].ion[i1].temperature.has_value, msg
         assert ids.profiles_1d[itime].ion[i1].velocity.diamagnetic.has_value, msg
         assert ids.profiles_1d[itime].ion[i1].velocity.poloidal.has_value, msg
         assert ids.profiles_1d[itime].ion[i1].velocity.toroidal.has_value, msg

      assert ids.profiles_1d[itime].j_bootstrap.has_value, msg
      assert ids.profiles_1d[itime].j_non_inductive.has_value, msg
      assert ids.profiles_1d[itime].j_ohmic.has_value, msg
      assert ids.profiles_1d[itime].j_total.has_value, msg
      assert ids.profiles_1d[itime].magnetic_shear.has_value, msg
      assert ids.profiles_1d[itime].pressure_ion_total.has_value, msg
      assert ids.profiles_1d[itime].pressure_parallel.has_value, msg
      assert ids.profiles_1d[itime].pressure_perpendicular.has_value, msg
      assert ids.profiles_1d[itime].pressure_thermal.has_value, msg
      assert ids.profiles_1d[itime].q.has_value, msg
      assert ids.profiles_1d[itime].t_i_average.has_value, msg
      assert ids.profiles_1d[itime].zeff.has_value, msg


@validator("core_profiles")
def validate_global_quantities_ip(ids):
   """Validate that global_quantities/ip(:) is in range of -17MA < ip <= 0."""
   for i in range(len(ids.global_quantities.ip)):
      ip = ids.global_quantities.ip[i]
      assert -17000000. < ip <= 0., f"global_quantities.ip[{i}]={ip} is not in range of -17MA < ip <= 0." 
