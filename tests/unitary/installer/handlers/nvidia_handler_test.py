from unittest.mock import patch

import pytest

from xmipp3_installer.installer.handlers import nvidia_handler

from .... import get_assertion_message

__DRIVER_VERSION_COMMAND = "nvidia-smi --query-gpu=driver_version --format=csv,noheader"

def test_calls_run_shell_command_when_getting_driver_version(__mock_run_shell_command):
  nvidia_handler.get_driver_version()
  __mock_run_shell_command.assert_called_once_with(__DRIVER_VERSION_COMMAND)

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_driver_version",
  [
    pytest.param((0, "550.54.15"), "550.54.15"),
    pytest.param((0, "550.54.15\n550.54.15"), "550.54.15"),
    pytest.param((0, "  535.104 \n"), "535.104"),
    pytest.param((0, "560"), "560"),
    pytest.param((1, "550.54.15"), None),
    pytest.param((127, ""), None),
    pytest.param((0, ""), None),
    pytest.param((0, "NVIDIA-SMI has failed"), None),
    pytest.param((0, "550.54."), None)
  ],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_driver_version(
  __mock_run_shell_command,
  expected_driver_version
):
  driver_version = nvidia_handler.get_driver_version()
  assert (
    driver_version == expected_driver_version
  ), get_assertion_message("driver version", expected_driver_version, driver_version)

@pytest.mark.parametrize(
  "driver_version,expected_is_valid",
  [
    pytest.param("550.54.15", True),
    pytest.param("560", True),
    pytest.param("525.x", False),
    pytest.param("550.54.", False),
    pytest.param("", False),
    pytest.param(525, False),
    pytest.param(None, False)
  ]
)
def test_returns_expected_driver_version_validity(driver_version, expected_is_valid):
  is_valid = nvidia_handler.is_valid_driver_version(driver_version)
  assert (
    is_valid == expected_is_valid
  ), get_assertion_message("driver version validity", expected_is_valid, is_valid)

@pytest.mark.parametrize(
  "driver_version,min_driver_version,expected_is_compatible",
  [
    pytest.param("550.54.15", "525.60.13", True),
    pytest.param("525.60.13", "525.60.13", True),
    pytest.param("1000.1", "999.99.99", True),
    pytest.param("525.60.13", "525.60.2", True),
    pytest.param("470.82.01", "525.60.13", False),
    pytest.param("525", "525.60", False),
    pytest.param("525.60.2", "525.60.13", False)
  ]
)
def test_returns_expected_driver_compatibility(
  driver_version,
  min_driver_version,
  expected_is_compatible
):
  is_compatible = nvidia_handler.is_driver_compatible(driver_version, min_driver_version)
  assert (
    is_compatible == expected_is_compatible
  ), get_assertion_message("driver compatibility", expected_is_compatible, is_compatible)

@pytest.mark.parametrize(
  "version,expected_version_numbers",
  [
    pytest.param("550", (550,)),
    pytest.param("550.54.15", (550, 54, 15)),
    pytest.param("470.82.01", (470, 82, 1))
  ]
)
def test_returns_expected_version_numbers(version, expected_version_numbers):
  version_numbers = nvidia_handler._get_version_numbers(version)
  assert (
    version_numbers == expected_version_numbers
  ), get_assertion_message("version numbers", expected_version_numbers, version_numbers)

@pytest.fixture
def __mock_run_shell_command(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = getattr(request, 'param', (0, "550.54.15"))
    yield mock_method
