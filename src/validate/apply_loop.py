"""
This file describes the validation loop in which the rules are applied to the
IDS data
"""

def get_ids_urls():
  """"""
  pass

def get_ids_data():
  """Lazily load ids-data and return"""
  urls = get_ids_urls()
  for url in url:
    ids_data = load_ids_data_from_url(url)
    yield ids_data

def validation_loop():
  """"""
  pass
