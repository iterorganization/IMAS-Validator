import imas
from imas.imasdef import MDSPLUS_BACKEND
import os
import numpy as np

URI = 'imas:mdsplus?' \
          f'user={os.getenv("USER")};' \
          'database=test;' \
          'shot=1;' \
          'run=2;' \
          'version=3'

entry              = imas.DBEntry(uri=URI, mode='w')
ids_core_profiles        = entry.get('core_profiles')

ids_core_profiles.ids_properties.homogeneous_time         = imas.imasdef.IDS_TIME_MODE_HOMOGENEOUS

ids_core_profiles.profiles_1d.rho_tor_norm = np.array([0,1,2,3,4,5,6,7,8,9])
ids_core_profiles.time = np.array([])

entry.put(ids_core_profiles)
