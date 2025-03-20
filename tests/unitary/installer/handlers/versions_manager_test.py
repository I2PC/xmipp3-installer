from unittest.mock import patch, mock_open

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.handlers.versions_manager import VersionsManager
from xmipp3_installer.shared import singleton

from .... import get_assertion_message

__FILE_PATH = "/path/to/version.json"
__VERSION_INFO = {
  constants.XMIPP: {
    "version_number": "3.23.1",
    "version_name": "v3.23.1-Godname",
    "release_date": "25/12/2023"
  },
  "sources_target_tag": {
    constants.XMIPP_CORE: "v1",
    constants.XMIPP_VIZ: "v2"
  }
}
__INVALID_VERSION_INFO = {
  **__VERSION_INFO,
  constants.XMIPP: {
    **__VERSION_INFO[constants.XMIPP],
    "version_number": "3.23",
  }
}
__INVALID_DATE_INFO = {
  **__VERSION_INFO,
  constants.XMIPP: {
    **__VERSION_INFO[constants.XMIPP],
    "release_date": "25-12-2023"
  }
}

def test_inherits_from_singleton_class(
  __mock_get_version_info,
  __mock_validate_fields
):
  version_manager = VersionsManager(__FILE_PATH)
  assert isinstance(version_manager, singleton.Singleton)

def test_sets_file_path_when_initializing(
  __mock_get_version_info,
  __mock_validate_fields
):
  version_manager = VersionsManager(__FILE_PATH)
  assert (
    version_manager.version_file_path == __FILE_PATH
  ), get_assertion_message(
    "version file path",
    __FILE_PATH,
    version_manager.version_file_path
  )

def test_sets_version_info_when_initializing(
  __mock_get_version_info,
  __mock_validate_fields
):
  version_manager = VersionsManager(__FILE_PATH)
  version_info = (
    version_manager.xmipp_version_number,
    version_manager.xmipp_version_name,
    version_manager.xmipp_release_date,
    version_manager.sources_versions
  )
  expected_version_info = (
    __VERSION_INFO[constants.XMIPP]["version_number"],
    __VERSION_INFO[constants.XMIPP]["version_name"],
    __VERSION_INFO[constants.XMIPP]["release_date"],
    __VERSION_INFO["sources_target_tag"]
  )
  assert (
    version_info == expected_version_info
  ), get_assertion_message("version info", expected_version_info, version_info)

def test_calls_get_version_info_when_initializing(
  __mock_get_version_info,
  __mock_validate_fields
):
  VersionsManager(__FILE_PATH)
  __mock_get_version_info.assert_called_once_with()

def test_calls_validate_fields_when_initializing(
  __mock_get_version_info,
  __mock_validate_fields
):
  VersionsManager(__FILE_PATH)
  __mock_validate_fields.assert_called_once_with()

def test_calls_open_when_getting_version_info(
  __mock_init,
  __mock_open
):
  VersionsManager(__FILE_PATH)._VersionsManager__get_version_info()
  __mock_open.assert_called_once_with(__FILE_PATH, encoding="utf-8")

def test_calls_json_load_when_getting_version_info(
  __mock_init,
  __mock_json_load,
  __mock_open
):
  VersionsManager(__FILE_PATH)._VersionsManager__get_version_info()
  __mock_json_load.assert_called_once_with(__mock_open())

def test_returns_loaded_json_when_getting_version_info(__mock_init, __mock_open):
  version_manager = VersionsManager(__FILE_PATH)
  version_info = version_manager._VersionsManager__get_version_info()
  assert (
    version_info == __VERSION_INFO
  ), get_assertion_message("version info", __VERSION_INFO, version_info)

@pytest.mark.parametrize(
  "__mock_init,expected_error_message",
  [
    pytest.param(
      __INVALID_VERSION_INFO,
      "Version number '3.23' is invalid. Must be three numbers separated by dots (x.y.z).",
      id="invalid_version"
    ),
    pytest.param(
      __INVALID_DATE_INFO,
      "Release date '25-12-2023' is invalid. Must be in dd/mm/yyyy format.",
      id="invalid_date"
    )
  ],
  indirect=["__mock_init"]
)
def test_raises_value_error_when_validating_invalid_fields(
  __mock_init,
  expected_error_message
):
  with pytest.raises(ValueError) as error:
    VersionsManager(__FILE_PATH)._VersionsManager__validate_fields()
  error_message = str(error.value)
  assert (
    error_message == expected_error_message
  ), get_assertion_message("ValueError message", expected_error_message, error_message)

def test_validates_version_numbers_successfully(__mock_init):
  VersionsManager(__FILE_PATH)._VersionsManager__validate_version_number()

@pytest.mark.parametrize(
  "version_number,valid",
  [
    pytest.param("1.2", False, id="two_numbers"),
    pytest.param("1.2.3.4", False, id="four_numbers"),
    pytest.param("1.2.a", False, id="non_numeric"),
    pytest.param("1..2", False, id="empty_number"),
    pytest.param("1.2.3", True, id="valid")
  ]
)
def test_returns_expected_semver_validation(__mock_init, version_number, valid):
  assert VersionsManager._VersionsManager__is_valid_semver(version_number.split('.')) == valid

def test_calls_datetime_strptime_when_validatingrelease_date(
  __mock_init,
  __mock_datetime
):
  version_manager = VersionsManager(__FILE_PATH)
  version_manager._VersionsManager__validate_release_date()
  __mock_datetime.strptime.assert_called_once_with(version_manager.xmipp_release_date, "%d/%m/%Y")

@pytest.fixture
def __mock_get_version_info():
  with patch(
    "xmipp3_installer.installer.handlers.versions_manager.VersionsManager._VersionsManager__get_version_info"
  ) as mock_method:
    mock_method.return_value = __VERSION_INFO
    yield mock_method

@pytest.fixture
def __mock_validate_fields():
  with patch(
    "xmipp3_installer.installer.handlers.versions_manager.VersionsManager._VersionsManager__validate_fields"
  ) as mock_method:
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_json_load():
  with patch("json.load") as mock_method:
    mock_method.return_value = __VERSION_INFO
    yield mock_method

@pytest.fixture
def __mock_open():
  m_open = mock_open()
  with patch("builtins.open", m_open):
    yield m_open

@pytest.fixture(params=[__VERSION_INFO])
def __mock_init(request):
  with patch(
    "xmipp3_installer.installer.handlers.versions_manager.VersionsManager.__init__",
    return_value=None
  ) as mock_method:
    version_manager = VersionsManager(__FILE_PATH)
    version_manager.version_file_path = __FILE_PATH
    version_manager.xmipp_version_number = request.param[constants.XMIPP]["version_number"]
    version_manager.xmipp_version_name = request.param[constants.XMIPP]["version_name"]
    version_manager.xmipp_release_date = request.param[constants.XMIPP]["release_date"]
    version_manager.sources_versions = request.param["sources_target_tag"]
    yield mock_method

@pytest.fixture
def __mock_datetime():
  with patch(
    "xmipp3_installer.installer.handlers.versions_manager.datetime"
  ) as mock_method:
    yield mock_method
