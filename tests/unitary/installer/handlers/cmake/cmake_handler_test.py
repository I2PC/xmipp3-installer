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

def test_does_not_call_which_when_getting_cmake_path_with_valid_cmake_key(__mock_which):
  cmake_handler.get_cmake_path({variables.CMAKE: __CMAKE_PATH})
  __mock_which.assert_not_called()

@pytest.mark.parametrize(
  "dictionary",
  [
    pytest.param({}),
    pytest.param({'key': True}),
    pytest.param({variables.CMAKE: None})
  ]
)
def test_calls_which_when_getting_cmake_path_with_invalid_cmake_key(
  dictionary,
  __mock_which
):
  cmake_handler.get_cmake_path(dictionary)
  __mock_which.assert_called_once_with(cmake_constants.DEFAULT_CMAKE)

@pytest.mark.parametrize(
  "dictionary,__mock_which,expected_cmake_path",
  [
    pytest.param({}, "test", "test"),
    pytest.param({variables.CMAKE: "something"}, None, "something"),
    pytest.param({variables.CMAKE: "something"}, "test", "something")
  ],
  indirect=["__mock_which"]
)
def test_returns_expected_cmake_path(
  dictionary,
  __mock_which,
  expected_cmake_path
):
  cmake_path = cmake_handler.get_cmake_path(dictionary)
  assert (
    cmake_path == expected_cmake_path
  ), get_assertion_message("CMake path", expected_cmake_path, cmake_path)

@pytest.mark.parametrize(
  "line,expected_library_version",
  [
    pytest.param("", {}),
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

def test_calls_open_when_getting_library_versions_from_cmake_file(__mock_open):
  cmake_handler.get_library_versions_from_cmake_file(__FILE_PATH)
  __mock_open.assert_called_once_with(__FILE_PATH, 'r')

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

def test_returns_expected_library_versions_from_cmake_file(__mock_open):
  library_versions = cmake_handler.get_library_versions_from_cmake_file(__FILE_PATH)
  assert (
    library_versions == __VERSIONS
  ), get_assertion_message("library versions", __VERSIONS, library_versions)

@pytest.fixture
def __mock_which(request):
  with patch("shutil.which") as mock_method:
    cmake_path = request.param if hasattr(request, "param") else __CMAKE_PATH
    mock_method.return_value = cmake_path
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