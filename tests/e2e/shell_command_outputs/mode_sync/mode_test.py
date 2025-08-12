import os
from typing import List

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.modes.mode_sync import mode_test_executor

from ... import shell_command_outputs
from ....test_files import xmipp_sync_data, test

BASHRC_FILE_NAME = "fake.bashrc"
NON_EXISTING_BASHRC_FILE_PATH = os.path.join(
  os.path.dirname(mode_test_executor._BASHRC_FILE_PATH),
  BASHRC_FILE_NAME
)
__NO_BASHRC_FILE_ERROR = f"File {NON_EXISTING_BASHRC_FILE_PATH} does not exist."
NON_BASHRC_FILE = logger.red(f"{__NO_BASHRC_FILE_ERROR}\n\n{shell_command_outputs.IO_ERROR_NO_FORMAT}") + "\n"

def get_test_messages_section(test_names: List[str]) -> str:
  if not test_names:
    return test.MESSAGE
  test_names_str = ', '.join(test_names)
  return f" Tests to run: {test_names_str}\n{test.MESSAGE}"

def get_download_message(test_params: str) -> str:
  test_names = test_params.split(" ") if test_params else []
  return "\n".join([
    logger.blue("Downloading the test files"),
    xmipp_sync_data.MESSAGE,
    get_test_messages_section(test_names),
    ""
	])

def get_update_message(test_params: str) -> str:
  test_names = test_params.split(" ") if test_params else []
  return "\n".join([
    logger.blue("Updating the test files"),
    get_test_messages_section(test_names),
    ""
	])
