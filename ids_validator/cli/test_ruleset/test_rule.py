@validator("core_profiles")
def validate(ids):
    assert ids.time.has_value
 #   assert ids.ids_properties.source.has_value
#    assert ids.ids_properties.provider.has_value
