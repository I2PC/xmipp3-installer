from unittest.mock import patch, Mock, call

import pytest

from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.installer import constants

from .... import get_assertion_message

__LINES = ["line1\n", "line2\n", "line3\n", "line4\n"]
__LOG_TAIL = ''.join(__LINES)
__ETH_MAC_ADDRESS = "00:08:9b:c4:30:31"
__IP_ADDR_LINES = [
  "1: Lo: <LOOPBACK, UP, LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN",
  "\tlink/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00",
  "\tinet 127.0.0.1/8 scope host lo",
  "\tinet6 ::1/128 scope host",
  "\t\tvalid_lft forever preferred_lft forever",
  "2: eth0: <BROADCAST, MULTICAST> mtu 1500 qdisc noop state DOWN qlen 1000",
  f"\tlink/ether {__ETH_MAC_ADDRESS} brd ff:ff:ff:ff:ff:ff",
  "3: eth1: <BROADCAST, MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000",
  "\tlink/ether 00:08:9b:c4:30:30 brd ff:ff:ff:ff:ff:ff",
  "\tinet 192.168.1.10/24 brd 192.168.1.255 scope global eth1",
  "\tineto fe80::208:9bff:fec4:3030/64 scope link",
  "\t\tvalid_lft forever preferred_lft forever"
]
__IP_ADDR_TEXT = '\n'.join(__IP_ADDR_LINES)

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
  __mock_re_match.return_value = None
  installation_info_assembler.__find_mac_address_in_lines(__LINES)
  __mock_re_match.assert_has_calls([
    call(
      r"^\d+: (enp|wlp|eth)\w+",
      line
    ) for line in __LINES[:-1]
  ])

def test_calls_re_match_group_when_finding_mac_address_in_lines(__mock_re_match):
  installation_info_assembler.__find_mac_address_in_lines(__LINES[:2])
  __mock_re_match().group.assert_called_once_with(1)

def test_calls_re_search_when_finding_mac_address_in_lines(__mock_re_match, __mock_re_search):
  __mock_re_match.return_value = __mock_re_groups("enp")
  installation_info_assembler.__find_mac_address_in_lines(__LINES[:2])
  __mock_re_search.assert_called_once_with(r"link/ether ([0-9a-f:]{17})", __LINES[1])

def test_calls_re_search_group_when_finding_mac_address_in_lines(__mock_re_match, __mock_re_search):
  __mock_re_match.return_value = __mock_re_groups("enp")
  installation_info_assembler.__find_mac_address_in_lines(__LINES[:2])
  __mock_re_search().group.assert_called_once_with(1)

@pytest.mark.parametrize(
  "input_lines,expected_mac_address",
  [
    pytest.param([], None),
    pytest.param([""], None),
    pytest.param(["something"], None),
    pytest.param([__IP_ADDR_LINES[5]], None),
    pytest.param(__IP_ADDR_LINES[0:2], None),
    pytest.param(__IP_ADDR_LINES[5:7], __ETH_MAC_ADDRESS),
    pytest.param(__IP_ADDR_LINES, __ETH_MAC_ADDRESS)
  ]
)
def test_returns_expected_result_when_finding_mac_address_in_lines(
  input_lines,
  expected_mac_address
):
  mac_address = installation_info_assembler.__find_mac_address_in_lines(input_lines)
  assert (
    mac_address == expected_mac_address
  ), get_assertion_message("MAC address", expected_mac_address, mac_address)

def test_calls_run_shell_command_when_getting_mac_address(__mock_run_shell_command):
  __mock_run_shell_command.return_value = (1, "")
  installation_info_assembler.__get_mac_address()
  __mock_run_shell_command.assert_called_once_with("ip addr")

@pytest.mark.parametrize(
  "output",
  [pytest.param(""), pytest.param("Test"), pytest.param("Test\n2")]
)
def test_calls_find_mac_address_in_lines_when_getting_mac_address(
  output,
  __mock_run_shell_command,
  __mock_find_mac_address_in_lines
):
  __mock_run_shell_command.return_value = (0, output)
  installation_info_assembler.__get_mac_address()
  __mock_find_mac_address_in_lines.assert_called_once_with(output.split("\n"))

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_mac_address",
  [
    pytest.param((1, ""), None),
    pytest.param((1, __IP_ADDR_TEXT), None),
    pytest.param((0, ""), None),
    pytest.param((0, __IP_ADDR_TEXT), "00:08:9b:c4:30:31")
  ],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_mac_address_when_getting_mac_address(
  __mock_run_shell_command,
  expected_mac_address
):
  mac_address = installation_info_assembler.__get_mac_address()
  assert (
    mac_address == expected_mac_address
  ), get_assertion_message("MAC address", expected_mac_address, mac_address)

def test_calls_get_mac_address_when_getting_user_id(__mock_get_mac_address):
  __mock_get_mac_address.return_value = None
  installation_info_assembler.__get_user_id()
  __mock_get_mac_address.assert_called_once_with()

def test_calls_hashlib_sha256_when_getting_user_id(
    __mock_get_mac_address,
    __mock_hashlib_sha256
  ):
  installation_info_assembler.__get_user_id()
  __mock_hashlib_sha256.assert_called_once_with()

def test_calls_hashlib_sha256_update_when_getting_user_id(
    __mock_get_mac_address,
    __mock_hashlib_sha256
  ):
  installation_info_assembler.__get_user_id()
  __mock_hashlib_sha256().update.assert_called_once_with(__mock_get_mac_address().encode())

def test_calls_hashlib_sha256_hexdigest_when_getting_user_id(
    __mock_get_mac_address,
    __mock_hashlib_sha256
  ):
  installation_info_assembler.__get_user_id()
  __mock_hashlib_sha256().hexdigest.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_get_mac_address,__mock_hashlib_sha256,expected_user_id",
  [
    pytest.param(None, None, None),
    pytest.param(None, "test-id", None),
    pytest.param(__ETH_MAC_ADDRESS, None, None),
    pytest.param(__ETH_MAC_ADDRESS, "test-id", "test-id")
  ],
  indirect=["__mock_get_mac_address", "__mock_hashlib_sha256"]
)
def test_returns_expected_user_id(
    __mock_get_mac_address,
    __mock_hashlib_sha256,
    expected_user_id
  ):
  user_id = installation_info_assembler.__get_user_id()
  assert (
    user_id == expected_user_id
  ), get_assertion_message("user id", expected_user_id, user_id)

@pytest.fixture(params=[(0, "")])
def __mock_run_shell_command(request):
  with patch(
    "xmipp3_installer.installer.handlers.shell_handler.run_shell_command"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

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

@pytest.fixture
def __mock_find_mac_address_in_lines():
  with patch(
    "xmipp3_installer.api_client.assembler.installation_info_assembler.__find_mac_address_in_lines"
  ) as mock_method:
    yield mock_method

@pytest.fixture(params=[__ETH_MAC_ADDRESS])
def __mock_get_mac_address(request):
  with patch(
    "xmipp3_installer.api_client.assembler.installation_info_assembler.__get_mac_address"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[None])
def __mock_hashlib_sha256(request):
  mock_sha256 = Mock()
  mock_sha256.update.return_value = None
  mock_sha256.hexdigest.return_value = request.param
  with patch("hashlib.sha256") as mock_method:
    mock_method.return_value = mock_sha256
    yield mock_method
