import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.shared import file_operations

from .. import get_assertion_message, create_versions_json_file

__COMPILATION_FILES_DIR = paths.get_source_path("test_so")
__SO_FILE = os.path.join(__COMPILATION_FILES_DIR, "test.so")
__OS_FILE = os.path.join(__COMPILATION_FILES_DIR, "test.os")
__O_FILE = os.path.join(__COMPILATION_FILES_DIR, "test.o")
__DUMMY_FILE = os.path.join(__COMPILATION_FILES_DIR, "dummy_file")
__BIN_FILE = os.path.join(paths.BINARIES_PATH, "bin_file")
__DIR_STRUCT_ROOT = os.path.join(
  paths.SOURCES_PATH,
  constants.XMIPP,
  "applications",
  "programs"
)
__EMPTY_DIR = "empty_dir"
__NON_EMPTY_DIR = "non_empty"
__DBLITE_FILE = "test.dblite"
__PYCACHE_ROOT = "pycache_root"

@pytest.mark.parametrize(
  "confirmation_text",
  [
    pytest.param("", id="No confirmation"),
    pytest.param("no", id="Cancelled confirmation"),
    pytest.param("Y", id="Wrong confirmation"),
    pytest.param("y", id="Correct confirmation")
  ]
)
def test_deletes_expected_files(__setup_environment, confirmation_text):
  remain = confirmation_text != "y"
  command_words = ["xmipp3_installer", modes.MODE_CLEAN_BIN]
  subprocess.run(
    command_words,
    capture_output=True,
    text=True,
    input=confirmation_text,
    check=False
  )
  
  for remaining_path in [
    __DBLITE_FILE,
    __SO_FILE,
    __OS_FILE,
    __O_FILE,
    os.path.join(__PYCACHE_ROOT, "__pycache__"),
    os.path.join(__DIR_STRUCT_ROOT, __EMPTY_DIR),
    paths.BUILD_PATH,
    paths.BINARIES_PATH
  ]:
    file_exists = os.path.exists(remaining_path)
    assert (
      file_exists == remain
    ), get_assertion_message(
      f"{remaining_path} existence",
      remain,
      file_exists
    )
  assert (
    os.path.exists(__DUMMY_FILE)
  ), f"{__DUMMY_FILE} must always remain."

def __create_file(path):
  with open(path, "w") as empty_file:
    empty_file.write("")

def __generate_compilation_files():
  os.makedirs(__COMPILATION_FILES_DIR, exist_ok=True)
  __create_file(__SO_FILE)
  __create_file(__OS_FILE)
  __create_file(__O_FILE)
  __create_file(__DUMMY_FILE)

def __generate_empty_dirs():
  os.makedirs(__DIR_STRUCT_ROOT, exist_ok=True)
  os.makedirs(
    os.path.join(__DIR_STRUCT_ROOT, __EMPTY_DIR),
    exist_ok=True
  )
  non_empty_dir = os.path.join(__DIR_STRUCT_ROOT, __NON_EMPTY_DIR)
  os.makedirs(non_empty_dir, exist_ok=True)
  __create_file(os.path.join(non_empty_dir, "file1"))

@pytest.fixture
def __setup_environment():
  try:
    __generate_compilation_files()
    __generate_empty_dirs()
    __create_file(__DBLITE_FILE)
    os.makedirs(os.path.join(__PYCACHE_ROOT, "__pycache__"), exist_ok=True)
    os.makedirs(paths.BUILD_PATH, exist_ok=True)
    create_versions_json_file()
    os.makedirs(paths.BINARIES_PATH, exist_ok=True)
    __create_file(__BIN_FILE)
    yield
  finally:
    file_operations.delete_paths([
      __COMPILATION_FILES_DIR,
      paths.get_source_path(constants.XMIPP),
      __DBLITE_FILE,
      __PYCACHE_ROOT,
      paths.BUILD_PATH,
      paths.VERSION_INFO_FILE,
      paths.BINARIES_PATH
    ])
