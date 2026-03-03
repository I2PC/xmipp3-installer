"""### Functions that interact with Conda via shell."""

from __future__ import annotations

import os


def get_conda_prefix_path() -> str | None:
  """
  ### Returns the path for the current Conda enviroment.

  #### Returns:
  - (str | None): Path for current Conda enviroment.
  """
  return os.environ.get('CONDA_PREFIX')
