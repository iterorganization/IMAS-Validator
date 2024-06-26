#
#

@validator("core_profiles")
def validate_global_quantities_ip(ids):
   """Validate that global_quantities/ip(:) is in range of -17MA < ip <= 0."""
   for i in range(len(ids.global_quantities.ip)):
      ip = ids.global_quantities.ip[i]
      assert -17000000. < ip <= 0., f"global_quantities.ip[{i}]={ip} is not in range of -17MA < ip <= 0." 
