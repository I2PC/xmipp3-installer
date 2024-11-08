from unittest.mock import patch, Mock, call

import pytest

from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.installer import constants

from .... import get_assertion_message

__LOG_TAIL = "line1\nline2\nline3\nline4\n"
__IP_ADDR_EXAMPLE = """1: Lo: <LOOPBACK, UP, LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
  link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
  inet 127.0.0.1/8 scope host lo
  inet6 ::1/128 scope host
    valid_lft forever preferred_lft forever
2: eth0: <BROADCAST, MULTICAST> mtu 1500 qdisc noop state DOWN qlen 1000
  link/ether 00:08:9b:c4:30:31 brd ff:ff:ff:ff:ff:ff
3: eth1: <BROADCAST, MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
  link/ether 00:08:9b:c4:30:30 brd ff:ff:ff:ff:ff:ff
  inet 192.168.1.10/24 brd 192.168.1.255 scope global eth1
  ineto fe80::208:9bff:fec4:3030/64 scope link
    valid_lft forever preferred_lft forever"""

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

def test_calls_run_shell_command_when_getting_log_tail(__mock_run_shell_command):
  installation_info_assembler.__get_log_tail()
  __mock_run_shell_command.assert_called_once_with(
    f"tail -n {constants.TAIL_LOG_NCHARS} {constants.LOG_FILE}"
  )

@pytest.mark.parametrize(
  "ret_code,n_chars,expected_log_tail",
  [
    pytest.param(1, 10, None),
    pytest.param(0, 10, __LOG_TAIL[:10]),
    pytest.param(0, 0, ""),
  ],
)
def test_returns_expected_log_tail(
  ret_code,
  n_chars,
  expected_log_tail,
  __mock_run_shell_command
):
  mocked_log_tail = ''.join([__LOG_TAIL[letter_index] for letter_index in range(n_chars)])
  __mock_run_shell_command.return_value = (ret_code, mocked_log_tail)
  log_tail = installation_info_assembler.__get_log_tail()
  assert (
    log_tail == expected_log_tail
  ), get_assertion_message("log tail", expected_log_tail, log_tail)

def test_does_not_call_re_match_when_finding_mac_address_in_lines_with_no_lines(__mock_re_match):
  installation_info_assembler.__find_mac_address_in_lines([])
  __mock_re_match.assert_not_called()

def test_calls_re_match_when_finding_mac_address_in_lines_with_valid_lines(__mock_re_match):
  lines = ["line1\n", "line2\n", "line3\n", "line4\n"]
  __mock_re_match.return_value = None
  installation_info_assembler.__find_mac_address_in_lines(lines)
  __mock_re_match.assert_has_calls([
    call(
      r"^\d+: (enp|wlp|eth)\w+",
      line
    ) for line in lines
  ])

def test_calls_re_match_group_when_finding_mac_address_in_lines(__mock_re_match):
  installation_info_assembler.__find_mac_address_in_lines(["line1\n"])
  __mock_re_match().group.assert_called_once_with(1)

def test_calls_re_search_when_finding_mac_address_in_lines(__mock_re_match, __mock_re_search):
  lines = ["line1\n", "line-to-find\n"]
  __mock_re_match.return_value = __mock_re_groups("enp")
  installation_info_assembler.__find_mac_address_in_lines(lines)
  __mock_re_search.assert_called_once_with(r"link/ether ([0-9a-f:]{17})", lines[1])

def test_calls_re_search_group_when_finding_mac_address_in_lines(__mock_re_match, __mock_re_search):
  lines = ["line1\n", "line-to-find\n"]
  __mock_re_match.return_value = __mock_re_groups("enp")
  installation_info_assembler.__find_mac_address_in_lines(lines)
  __mock_re_search().group.assert_called_once_with(1)

@pytest.mark.parametrize(
  "__mock_re_match,__mock_re_search,expected_mac_address",
  [
    pytest.param("", "", None),
    pytest.param("", "something", None),
    pytest.param("something", "", None),
    pytest.param("something", "something", None),
    pytest.param("eth", "something", "something"),
    pytest.param("enp", "something", "something"),
    pytest.param("wlp", "something", "something")
  ],
  indirect=["__mock_re_match", "__mock_re_search"]
)
def test_returns_expected_result_when_finding_mac_address_in_lines(
  __mock_re_match,
  __mock_re_search,
  expected_mac_address
):
  mac_address = installation_info_assembler.__find_mac_address_in_lines([""])
  assert (
    mac_address == expected_mac_address
  ), get_assertion_message("MAC address", expected_mac_address, mac_address)

@pytest.fixture
def __mock_run_shell_command(request):
  ret_code, output = request.param if hasattr(request, "param") else (0, "")
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = (ret_code, output)
    yield mock_method

#@pytest.fixture
#def __mock_get_mac_address():
#  with patch(
#    "xmipp3_installer.api_client.assembler.installation_info_assembler.__get_mac_address"
#  ) as mock_method:
#    yield mock_method

def __mock_re_groups(group_value):
  groups = Mock()
  groups.group.side_effect = lambda _: group_value
  return groups

@pytest.fixture(params=[""])
def __mock_re_match(request):
  with patch("re.match") as mock_method:
    mock_method.return_value = __mock_re_groups(request.param)
    yield mock_method

@pytest.fixture(params=([""]))
def __mock_re_search(request):
  with patch("re.search") as mock_method:
    mock_method.return_value = __mock_re_groups(request.param)
    yield mock_method
