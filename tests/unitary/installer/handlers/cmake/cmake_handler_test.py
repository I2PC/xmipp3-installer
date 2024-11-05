from unittest.mock import patch

import pytest

from xmipp3_installer.installer.handlers.cmake import cmake_handler
from xmipp3_installer.installer.handlers.cmake import cmake_constants
from xmipp3_installer.repository.config_vars import variables

from ..... import get_assertion_message

__CMAKE_PATH = "/path/to/cmake"

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

@pytest.fixture
def __mock_which(request):
  with patch("shutil.which") as mock_method:
    cmake_path = request.param if hasattr(request, "param") else __CMAKE_PATH
    mock_method.return_value = cmake_path
    yield mock_method
