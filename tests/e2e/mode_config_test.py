import filecmp
import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.repository.config_vars import variables
from xmipp3_installer.repository.config import ConfigurationFileHandler
from xmipp3_installer.shared import file_operations

from .. import (
  get_file_content, normalize_file_line_endings,
  get_test_file, copy_file_from_reference, create_versions_json_file
)

__DATE = "10-12-2024 17:26.33"

@pytest.mark.parametrize(
  "__setup_config_evironment,expected_file,overwrite",
  [
    pytest.param((False, "default.conf"), "default.conf", False, id="New file without overwrite"),
    pytest.param((True, "default.conf"), "default.conf", False, id="Existing default file without overwrite"),
    pytest.param((True, "modified.conf"), "modified.conf", False, id="Existing modified file without overwrite"),
    pytest.param((True, "unknown.conf"), "unknown.conf", False, id="Existing unknown variables file without overwrite"),
    pytest.param((False, "default.conf"), "default.conf", True, id="New file with overwrite"),
    pytest.param((True, "default.conf"), "default.conf", True, id="Existing default file with overwrite"),
    pytest.param((True, "modified.conf"), "default.conf", True, id="Existing modified file with overwrite"),
    pytest.param((True, "unknown.conf"), "default.conf", True, id="Existing unknown variables file with overwrite")
  ],
  indirect=["__setup_config_evironment"]
)
def test_writes_expected_config_file(
  __setup_config_evironment,
  expected_file,
  overwrite
):
  command_words = ["xmipp3_installer", modes.MODE_CONFIG]
  if overwrite:
    command_words.append("-o")
  subprocess.run(command_words, stdout=subprocess.PIPE, check=False)
  __change_config_file_date()
  __change_config_cmake_path()
  copy_file_from_reference(
    __get_test_config_file(expected_file, False),
    __setup_config_evironment
  )
  normalize_file_line_endings(__setup_config_evironment)
  assert (
    filecmp.cmp(
      paths.CONFIG_FILE,
      __setup_config_evironment,
      shallow=False
    )
  ), f"Expected:\n{get_file_content(__setup_config_evironment)}\n\nReceived:\n{get_file_content(paths.CONFIG_FILE)}"

def __get_test_config_file(file_name, input):
  return get_test_file(
    os.path.join(
      "conf-files",
      "input" if input else "output",
      file_name
    )
  )

def __change_config_file_date():
  file_hanlder = ConfigurationFileHandler()
  old_date = file_hanlder.get_config_date()
  content = get_file_content(paths.CONFIG_FILE)
  with open(paths.CONFIG_FILE, 'w') as config_file:
    content = content.replace(old_date, __DATE)
    config_file.write(content)

def __change_config_cmake_path():
  content = get_file_content(paths.CONFIG_FILE)
  new_content_lines = []
  for line in content.splitlines(keepends=True):
    if line.startswith(variables.PREFIX_PATH):
      line = f"{variables.PREFIX_PATH}=\n"
    new_content_lines.append(line)
  content = "".join(new_content_lines)
  with open(paths.CONFIG_FILE, 'w') as config_file:
    config_file.write(content)

@pytest.fixture(params=[(False, "default.conf")])
def __setup_config_evironment(request):
  exists, copy_name = request.param
  try:
    create_versions_json_file()
    if not exists:
      file_operations.delete_paths([paths.CONFIG_FILE, copy_name])
    else:
      copy_file_from_reference(
        __get_test_config_file(copy_name, True),
        paths.CONFIG_FILE
      )
    yield copy_name
  finally:
    file_operations.delete_paths([
      paths.CONFIG_FILE,
      copy_name,
      paths.VERSION_INFO_FILE
    ])
