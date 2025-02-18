import json
import os

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.handlers import versions_manager
from xmipp3_installer.shared import file_operations

from .... import copy_file_from_reference, get_test_file

@pytest.mark.parametrize(
  "__setup_environment",
  [
    pytest.param((False, "valid")),
    pytest.param((False, "syntax-error"))
  ],
  indirect=["__setup_environment"]
)
def test_raises_io_error_when_json_file_does_not_exist(__setup_environment):
  with pytest.raises(IOError):
    versions_manager.VersionsManager(constants.VERSION_INFO_FILE)

@pytest.mark.parametrize(
  "__setup_environment",
  [pytest.param((True, "syntax-error"))],
  indirect=["__setup_environment"]
)
def test_raises_json_decode_error_when_json_file_is_not_properly_formatted(__setup_environment):
  with pytest.raises(json.JSONDecodeError):
    versions_manager.VersionsManager(constants.VERSION_INFO_FILE)

@pytest.mark.parametrize(
  "__setup_environment",
  [
    pytest.param((True, "invalid-date")),
    pytest.param((True, "invalid-version"))
  ],
  indirect=["__setup_environment"]
)
def test_raises_value_error_when_fields_are_not_valid(__setup_environment):
  with pytest.raises(ValueError):
    versions_manager.VersionsManager(constants.VERSION_INFO_FILE)

def test_reads_expected_json_file(__setup_environment):
  versions_manager.VersionsManager(constants.VERSION_INFO_FILE)

@pytest.fixture(params=[(True, "valid")])
def __setup_environment(request):
  exists, file_name = request.param
  file_name = f"{file_name}.json"
  try:
    if exists:
      copy_file_from_reference(
        get_test_file(
          os.path.join(
            "version_info_files",
            file_name
          )
        ),
        constants.VERSION_INFO_FILE
      )
    else:
      file_operations.delete_paths([
        constants.VERSION_INFO_FILE
      ])
    yield exists, file_name
  finally:
    file_operations.delete_paths([
      constants.VERSION_INFO_FILE
    ])
