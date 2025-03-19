from unittest.mock import patch

import pytest

from xmipp3_installer.installer.handlers import generic_package_handler

from .... import get_assertion_message

@pytest.mark.parametrize(
  "package_name",
  [pytest.param("my-package"), pytest.param("other-package")]
)
def test_calls_run_shell_command_when_getting_package_version(
  package_name,
  __mock_run_shell_command
):
  generic_package_handler.get_package_version(package_name)
  __mock_run_shell_command.assert_called_once_with(f"{package_name} --version")

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_package_version",
  [
    pytest.param((1, None), None),
    pytest.param((1, ""), None),
    pytest.param((1, "1.0.0"), None),
    pytest.param((0, None), None),
    pytest.param((0, ""), ""),
    pytest.param((0, "1.0.0"), "1.0.0")
  ],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_result_when_getting_package_version(
  __mock_run_shell_command,
  expected_package_version
):
  package_version = generic_package_handler.get_package_version("test")
  assert (
    package_version == expected_package_version
  ), get_assertion_message("package version", expected_package_version, package_version)

@pytest.fixture(params=[(0, "default_output")])
def __mock_run_shell_command(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method
