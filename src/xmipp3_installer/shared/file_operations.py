"""# Module containing file-related functions."""

import os
import shutil
from typing import List

def delete_paths(paths: List[str]):
  """
  ### Deletes all the given paths (files or directories).

  #### Params:
  - path (list(str)): List of paths to delete.
  """
  for path in paths:
    if not os.path.exists(path):
      continue
    if os.path.isdir(path):
      shutil.rmtree(path, ignore_errors=True)
    else:
      os.remove(path)
