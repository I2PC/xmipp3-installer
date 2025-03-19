"""### Functions that interact with Conda via shell."""

import os
from typing import Optional

def get_conda_prefix_path() -> Optional[str]:
  """
  ### Returns the path for the current Conda enviroment.

  #### Returns:
  - (str | None): Path for current Conda enviroment.
  """
  return os.environ.get('CONDA_PREFIX')
