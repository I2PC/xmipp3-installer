from unittest.mock import patch

import pytest

from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.installer import constants

from .... import get_assertion_message

def test_calls_run_shell_command_when_getting_architecture_name(__mock_run_shell_command):
  installation_info_assembler.__get_architecture_name()
  __mock_run_shell_command.assert_called_once_with('cat /sys/devices/cpu/caps/pmu_name')

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_architecture_name",
  [
    pytest.param((1, "test-arch"), constants.UNKNOWN_VALUE),
    pytest.param((0, None), constants.UNKNOWN_VALUE),
    pytest.param((0, ""), constants.UNKNOWN_VALUE),
    pytest.param((0, "test-arch"), "test-arch")
  ],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_architecture_name(
  __mock_run_shell_command,
  expected_architecture_name
):
  architecture_name = installation_info_assembler.__get_architecture_name()
  assert (
    architecture_name == expected_architecture_name
  ), get_assertion_message("architecture name", expected_architecture_name, architecture_name)

@pytest.fixture
def __mock_get_mac_address():
  with patch(
    "xmipp3_installer.api_client.assembler.installation_info_assembler.__get_mac_address"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_run_shell_command(request):
  ret_code, output = request.param if hasattr(request, "param") else (0, "")
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = (ret_code, output)
    yield mock_method
