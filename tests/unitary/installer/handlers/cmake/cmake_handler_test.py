from unittest.mock import patch, call, mock_open

import pytest

from xmipp3_installer.installer.handlers.cmake import cmake_handler
from xmipp3_installer.installer.handlers.cmake import cmake_constants
from xmipp3_installer.repository.config_vars import variables

from ..... import get_assertion_message

__CMAKE_PATH = "/path/to/cmake"
__FILE_PATH = "test-file.txt"
__KEY1 = "var1"
__KEY2 = "var2"
__KEY3 = "other-var"
__VERSIONS = {
  __KEY1: "value1",
  __KEY2: "test",
  __KEY3: "testvalue"
}
__STREAM_READLINES = [
  f"{__KEY1}={__VERSIONS[__KEY1]}\n",
  f"{__KEY2}={__VERSIONS[__KEY2]}\n",
  f"{__KEY3}={__VERSIONS[__KEY3]}\n"
]

def test_calls_which_when_getting_cmake_path(
  __mock_which
):
  cmake_handler.get_cmake_path()
  __mock_which.assert_called_once_with(cmake_constants.DEFAULT_CMAKE)

@pytest.mark.parametrize(
  "__mock_which,expected_cmake_path",
  [
    pytest.param("test", "test"),
    pytest.param(None, None)
  ],
  indirect=["__mock_which"]
)
def test_returns_expected_cmake_path(
  __mock_which,
  expected_cmake_path
):
  cmake_path = cmake_handler.get_cmake_path()
  assert (
    cmake_path == expected_cmake_path
  ), get_assertion_message("CMake path", expected_cmake_path, cmake_path)

@pytest.mark.parametrize(
  "line,expected_library_version",
  [
    pytest.param("", {}),
    pytest.param("\n", {}),
    pytest.param("a=a=a", {}),
    pytest.param("==", {}),
    pytest.param("TEST=1", {"TEST": "1"}),
    pytest.param("TEST=1\n", {"TEST": "1"}),
    pytest.param("TEST=", {"TEST": None}),
    pytest.param("TEST=\n", {"TEST": None})
  ]
)
def test_gets_expected_library_version_from_line(line, expected_library_version):
  library_version = cmake_handler.__get_library_version_from_line(line)
  assert (
    library_version == expected_library_version
  ), get_assertion_message("library version", expected_library_version, library_version)

def test_calls_open_if_library_version_file_exists_when_getting_library_versions_from_cmake_file(__mock_open):
  cmake_handler.get_library_versions_from_cmake_file(__FILE_PATH)
  __mock_open.assert_called_once_with(__FILE_PATH, encoding="utf-8")

def test_does_not_call_open_if_library_version_file_does_not_exist_when_getting_library_versions_from_cmake_file(
  __mock_open,
  __mock_os_path_exists
):
  __mock_os_path_exists.return_value = False
  cmake_handler.get_library_versions_from_cmake_file(__FILE_PATH)
  __mock_open.assert_not_called()

def test_calls_get_library_version_from_line_when_getting_library_versions_from_cmake_file(
  __mock_open,
  __mock_get_library_version_from_line
):
  cmake_handler.get_library_versions_from_cmake_file(__FILE_PATH)
  __mock_get_library_version_from_line.assert_has_calls([
    call(__STREAM_READLINES[0]),
    call(__STREAM_READLINES[1]),
    call(__STREAM_READLINES[2])
  ])

@pytest.mark.parametrize(
  "__mock_os_path_exists,expected_versions",
  [pytest.param(False, {}), pytest.param(True, __VERSIONS)],
  indirect=["__mock_os_path_exists"]
)
def test_returns_expected_library_versions_from_cmake_file(
  __mock_os_path_exists,
  expected_versions,
  __mock_open
):
  library_versions = cmake_handler.get_library_versions_from_cmake_file(__FILE_PATH)
  assert (
    library_versions == expected_versions
  ), get_assertion_message("library versions", expected_versions, library_versions)

@pytest.mark.parametrize(
  "config_dict,__mock_internal_logic_vars,expected_cmake_vars",
  [
    pytest.param({}, [], ""),
    pytest.param({"var1": "somevalue"}, [], "-Dvar1=somevalue"),
    pytest.param({"var1": "somevalue"}, ["var1"], ""),
    pytest.param({"var1": "somevalue", "var2": "othervalue"}, ["var1"], "-Dvar2=othervalue"),
    pytest.param({"var1": "test", "var2": "test2"}, [], "-Dvar1=test -Dvar2=test2")
  ],
  indirect=["__mock_internal_logic_vars"]
)
def test_returns_expected_cmake_vars_str(
  config_dict,
  __mock_internal_logic_vars,
  expected_cmake_vars
):
  cmake_vars = cmake_handler.get_cmake_vars_str(config_dict)
  assert (
    cmake_vars == expected_cmake_vars
  ), get_assertion_message("CMake variables string", expected_cmake_vars, cmake_vars)

@pytest.fixture(params=[__CMAKE_PATH])
def __mock_which(request):
  with patch("shutil.which") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_open():
  m_open = mock_open(read_data=''.join(__STREAM_READLINES))
  with patch("builtins.open", m_open):
    yield m_open

@pytest.fixture
def __mock_get_library_version_from_line():
  with patch(
    "xmipp3_installer.installer.handlers.cmake.cmake_handler.__get_library_version_from_line"
  ) as mock_method:
    mock_method.return_value = {"test": "test"}
    yield mock_method

@pytest.fixture(params=[["internal-var1", "internal-var2"]])
def __mock_internal_logic_vars(request):
  with patch.object(variables, "INTERNAL_LOGIC_VARS", request.param):
    yield

@pytest.fixture(params=[True], autouse=True)
def __mock_os_path_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method
