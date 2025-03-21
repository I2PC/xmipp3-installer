import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.shared import file_operations

from .. import get_assertion_message, create_versions_json_file

@pytest.mark.parametrize(
  "confirmation_text",
  [
    pytest.param("", id="No confirmation"),
    pytest.param("no", id="Cancelled confirmation"),
    pytest.param("Yes", id="Wrong confirmation"),
    pytest.param("YeS", id="Correct confirmation")
  ]
)
def test_deletes_expected_files(__setup_environment, confirmation_text):
  remain = confirmation_text != "YeS"
  command_words = ["xmipp3_installer", modes.MODE_CLEAN_ALL]
  subprocess.run(
    command_words,
    capture_output=True,
    text=True,
    input=confirmation_text,
    check=False
  )
  
  for remaining_path in [
    *paths.XMIPP_SOURCE_PATHS,
    paths.INSTALL_PATH,
    paths.BUILD_PATH,
    paths.CONFIG_FILE
  ]:
    file_exists = os.path.exists(remaining_path)
    assert (
      file_exists == remain
    ), get_assertion_message(
      f"{remaining_path} existence",
      remain,
      file_exists
    )

def __create_config_file():
  with open(paths.CONFIG_FILE, "w") as empty_file:
    empty_file.write("")

@pytest.fixture
def __setup_environment():
  try:
    for source in paths.XMIPP_SOURCE_PATHS:
      os.makedirs(source, exist_ok=True)
    os.makedirs(paths.INSTALL_PATH, exist_ok=True)
    os.makedirs(paths.BUILD_PATH, exist_ok=True)
    __create_config_file()
    create_versions_json_file()
    yield
  finally:
    file_operations.delete_paths([
      *paths.XMIPP_SOURCE_PATHS,
      paths.INSTALL_PATH,
      paths.BUILD_PATH,
      paths.VERSION_INFO_FILE
    ])
