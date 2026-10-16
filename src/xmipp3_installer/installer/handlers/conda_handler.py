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

def get_conda_executable() -> str | None:
  """
  ### Returns the path to the Conda executable that activated the current environment.

  #### Returns:
  - (str | None): Path to the Conda executable.
  """
  return os.environ.get('CONDA_EXE')

def get_cuda_compiler_path() -> str | None:
  """
  ### Returns the path to the CUDA compiler installed in the current Conda environment.

  #### Returns:
  - (str | None): Path to nvcc, or None if there is no active environment or it has no nvcc.
  """
  conda_prefix = get_conda_prefix_path()
  if not conda_prefix:
    return None
  nvcc_path = os.path.join(conda_prefix, "bin", "nvcc")
  return nvcc_path if os.path.isfile(nvcc_path) else None

def get_environment_update_command(conda_executable: str, conda_prefix: str, environment_file: str) -> str:
  """
  ### Returns the command that installs the given environment file into the given Conda environment.

  `--prune` is deliberately not used, as it would uninstall packages not present
  in the file, such as this installer itself.

  #### Params:
  - conda_executable (str): Path to the Conda executable.
  - conda_prefix (str): Path to the Conda environment.
  - environment_file (str): Path to the Conda environment file.

  #### Returns:
  - (str): The command.
  """
  return f'"{conda_executable}" env update --prefix "{conda_prefix}" --file "{environment_file}"'
