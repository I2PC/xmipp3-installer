import os

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants, urls

from .. import mode_sync
from ...test_files import xmipp_sync_data, test

REAL_MODELS_DIR = os.path.join(constants.SOURCES_PATH, constants.XMIPP, "models")
FAKE_SYNC_PROGRAM_FULL_PATH = os.path.join(".", "tests", "e2e", "test_files", mode_sync.SYNC_PROGRAM_NAME)

def get_test_messages_section(test_names: str) -> str:
  test_names_str = ' '.join(test_names)
  return f" Tests to run: {test_names_str}\n{test.MESSAGE}"

__DOWNLOAD_SECTION = '\n'.join([
	logger.blue("Downloading the test files"),
  xmipp_sync_data.MESSAGE
])

__UPDATE_SECTION = '\n'.join([
  logger.blue("Updating the test files"),
  xmipp_sync_data.MESSAGE
])

def get_download_message(test_params: str) -> str:
  test_names = test_params.split(" ")
  return "\n".join([
    __DOWNLOAD_SECTION,
    get_test_messages_section(test_names),
    ""
	])

def get_update_message(test_params: str) -> str:
  test_names = test_params.split(" ")
  return "\n".join([
    __UPDATE_SECTION,
    get_test_messages_section(test_names),
    ""
	])
