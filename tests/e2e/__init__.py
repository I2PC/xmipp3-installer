from __future__ import annotations

import os
import shutil
import subprocess

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths

from .. import get_test_file

def copy_cmake_project(project_name: str) -> str:
  """
  ### Copies the given CMake project into the current directory.

  #### Params:
  - project_name (str): Name of the project.

  #### Returns:
  - (str): Absolute path to the copied project.
  """
  return os.path.abspath(
    shutil.copytree(
      get_test_file(os.path.join("cmake-cases", project_name)),
      project_name
    )
  )

def get_source_paths() -> list[str]:
  """
  ### Returns the paths to Xmipp's sources, relative to the current directory.

  `paths.XMIPP_SOURCE_PATHS` can't be used, as it is resolved against the directory tests are launched from.

  #### Returns:
  - (list(str)): Paths to the sources.
  """
  return [os.path.join(paths.SOURCES_PATH, source) for source in constants.XMIPP_SOURCES]

def init_git_repository():
  """
  ### Turns the current directory into a git repository with one commit.

  Xmipp's sources are looked up inside it, so git commands run on them have a branch and a commit to show.
  """
  subprocess.run(["git", "init", "-q", "-b", constants.MAIN_BRANCHNAME], check=True)
  subprocess.run(
    ["git", "-c", "user.name=test", "-c", "user.email=test", "commit", "-q", "--allow-empty", "-m", "Initial commit"],
    check=True
  )
