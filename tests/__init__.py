import os
import shutil
from typing import Any

from xmipp3_installer.installer.constants import paths

TEST_FILES_DIR = os.path.join(
  os.path.dirname(os.path.abspath(__file__)),
  "test_files"
)
JSON_XMIPP_VERSION_NUMBER = "3.25.0"
JSON_XMIPP_VERSION_NAME = f"v{JSON_XMIPP_VERSION_NUMBER}-TBD"
JSON_XMIPP_RELEASE_DATE = "01/01/2000"
JSON_XMIPP_CORE_TARGET_TAG = "v3"
JSON_XMIPP_VIZ_TARGET_TAG = "v3"

def get_assertion_message(item: str, expected: Any, received: Any) -> str:
  """
  ### Returns the assertion message for a given item and values.

  #### Params:
  - item (str): Item to compare.
  - expected (any): Expected value.
  - received (any): Received value.

  #### Returns:
  - (str): Assertion message for the given item.
  """
  return f"Received different {item} than expected.\nExpected: {expected}\nReceived: {received}"

class MockTerminalSize:
  """### This class is used to mock the terminal width."""
  def __init__(self, columns):
    self.columns = columns
  def __iter__(self):
    return iter((self.columns, 5))

def get_file_content(file_path: str) -> str:
  """
  ### Reads the content of the given file

  #### Params:
  - file_path (str): Path to the file

  #### Returns:
  - (str): Content of the file.
  """
  with open(file_path, "r") as config_file:
    return config_file.read()

def normalize_text_line_endings(text: str) -> str:
  """
  ### Adapts the content of a text for different OSs.

  #### Params:
  - text (str): Text to adapt.
  """
  return text.replace('\r\n', '\n')

def normalize_file_line_endings(file_path: str):
  """
  ### Adapts the content of a file for different OSs.

  #### Params:
  - file_path (str): Path to the file.
  """
  content = get_file_content(file_path)
  content = normalize_text_line_endings(content)
  with open(file_path, 'w') as file:
    file.write(content)

def copy_file_from_reference(source_file: str, dest_file: str):
  """
  ### Copies the input reference file into the destination file.

  #### Params:
  - source_file (str): Input reference file.
  - dest_file (str): Destination file.
  """
  file_directory = os.path.dirname(dest_file)
  if file_directory:
    os.makedirs(file_directory, exist_ok=True)
  shutil.copyfile(source_file, dest_file)

def get_test_file(file_path: str):
  """
  ### Returns the absoulte path to a file inside the tests folder.

  #### Params:
  - file_path (str): Path to the file relative to the root of tests.

  #### Returns:
  - (str): Absolute path to the given file.
  """
  return os.path.join(
    TEST_FILES_DIR,
    file_path
  )

def create_versions_json_file(output_path: str=None):
  """
  ### Generates a valid JSON versions file.
  """
  full_output_path = os.path.join(
    output_path,
    paths.VERSION_INFO_FILE
  ) if output_path else paths.VERSION_INFO_FILE
  copy_file_from_reference(
    get_test_file(
      os.path.join(
        "version-info-files",
        "valid.json"
      )
    ),
    full_output_path
  )
