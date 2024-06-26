#

@validator("summary")
def validate_global_quantities_b0(ids):
   """Validate that global_quantities/b0/value(:) is b0 < 0."""
   for i in range(len(ids.global_quantities.b0.value)):
      b0 = ids.global_quantities.b0.value[i]
      assert b0 < 0., f"global_quantities.b0.value[{i}]={b0} is not b0 < 0." 


@validator("summary")
def validate_global_quantities_ip(ids):
   """Validate that global_quantities/ip/value(:) is -17000000 < ip <= 0."""
   for i in range(len(ids.global_quantities.ip.value)):
      ip = ids.global_quantities.ip.value[i]
      assert -17000000 < ip <= 0., f"global_quantities.ip.value[{i}]={ip} is not -17000000 < ip <= 0."

