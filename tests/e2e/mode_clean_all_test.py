import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer import constants
from xmipp3_installer.repository import file_operations

from .. import get_assertion_message

@pytest.mark.parametrize(
  "confirmation_text",
  [
    pytest.param(""),
    pytest.param("no"),
    pytest.param("Yes"),
    pytest.param("YeS")
  ]
)
def test_deletes_expected_files(__setup_environment, confirmation_text):
  remain = confirmation_text != "YeS"
  command_words = ["xmipp3_installer", modes.MODE_CLEAN_ALL]
  subprocess.run(
    command_words,
    capture_output=True,
    text=True,
    input=confirmation_text
  )
  
  for remaining_path in [
    constants.XMIPP_CORE_PATH,
    constants.INSTALL_PATH,
    constants.BUILD_PATH,
    constants.CONFIG_FILE
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
  with open(constants.CONFIG_FILE, "w") as empty_file:
    empty_file.write("")

@pytest.fixture
def __setup_environment():
  try:
    os.makedirs(constants.XMIPP_CORE_PATH, exist_ok=True)
    os.makedirs(constants.INSTALL_PATH, exist_ok=True)
    os.makedirs(constants.BUILD_PATH, exist_ok=True)
    __create_config_file()
    yield
  finally:
    file_operations.delete_paths([
      constants.XMIPP_CORE_PATH,
      constants.INSTALL_PATH,
      constants.BUILD_PATH,
    ])
