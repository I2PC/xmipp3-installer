from xmipp3_installer.application.logger.logger import logger

from ....test_files import xmipp_sync_data, test

def get_test_messages_section(test_names: str) -> str:
  test_names_str = ' '.join(test_names)
  return f" Tests to run: {test_names_str}\n{test.MESSAGE}"

def get_download_message(test_params: str) -> str:
  test_names = test_params.split(" ")
  return "\n".join([
    logger.blue("Downloading the test files"),
    xmipp_sync_data.MESSAGE,
    get_test_messages_section(test_names),
    ""
	])

def get_update_message(test_params: str) -> str:
  test_names = test_params.split(" ")
  return "\n".join([
    logger.blue("Updating the test files"),
    get_test_messages_section(test_names),
    ""
	])
