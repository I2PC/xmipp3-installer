from unittest.mock import patch, Mock, call

import pytest

from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.installer.handlers import git_handler
from xmipp3_installer.installer.handlers.cmake import cmake_constants

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
__USER_ID = "test-user-id"
__PLATFORM_SYSTEM_WINDOWS = "Windows"
__PLATFORM_RELEASE_WINDOWS = "10"
__RELEASE_NAME_WINDOWS = f"{__PLATFORM_SYSTEM_WINDOWS} {__PLATFORM_RELEASE_WINDOWS}"
__PLATFORM_SYSTEM_LINUX = "Linux"
__DISTRO_NAME = "Ubuntu"
__DISTRO_VERSION = "24.04"
__RELEASE_NAME_LINUX = f"{__DISTRO_NAME} {__DISTRO_VERSION}"
__LIBRARY_VERSIONS = {
  cmake_constants.CMAKE_CUDA: "12.2",
  cmake_constants.CMAKE_CMAKE: "3.16",
  cmake_constants.CMAKE_GCC: "12.3",
  cmake_constants.CMAKE_GPP: "12.3",
  cmake_constants.CMAKE_MPI: "2.0",
  cmake_constants.CMAKE_PYTHON: "3.8",
  cmake_constants.CMAKE_SQLITE: "3.2",
  cmake_constants.CMAKE_JAVA: "2.4.5",
  cmake_constants.CMAKE_HDF5: "1.2.3",
  cmake_constants.CMAKE_JPEG: "3.2.1"
}
__ENVIROMENT_INFO = [
  ["flag1", "flag2"],
  "devel",
  True,
  False,
  __LOG_TAIL
]
__INSTALLATION_INFO = {
  "user": {
    "userId": __USER_ID
  },
  "version": {
    "os": __RELEASE_NAME_LINUX,
    "cpuFlags": __ENVIROMENT_INFO[0],
    "cuda": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_CUDA),
    "cmake": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_CMAKE),
    "gcc": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_GCC),
    "gpp": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_GPP),
    "mpi": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_MPI),
    "python": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_PYTHON),
    "sqlite": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_SQLITE),
    "java": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_JAVA),
    "hdf5": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_HDF5),
    "jpeg": __LIBRARY_VERSIONS.get(cmake_constants.CMAKE_JPEG)
  },
  "xmipp": {
    "branch": __ENVIROMENT_INFO[1],
    "updated": __ENVIROMENT_INFO[2],
    "installedByScipion": __ENVIROMENT_INFO[3]
  },
  "returnCode": 0,
  "logTail": __ENVIROMENT_INFO[4]
}
__EMPTY_INSTALLATION_INFO = {
  "user": {
    "userId": __USER_ID
  },
  "version": {
    "os": __RELEASE_NAME_LINUX,
    "cpuFlags": None,
    "cuda": None,
    "cmake": None,
    "gcc": None,
    "gpp": None,
    "mpi": None,
    "python": None,
    "sqlite": None,
    "java": None,
    "hdf5": None,
    "jpeg": None
  },
  "xmipp": {
    "branch": versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY],
    "updated": None,
    "installedByScipion": None
  },
  "returnCode": 0,
  "logTail": None
}

def test_calls_run_shell_command_when_getting_cpu_flags(__mock_run_shell_command):
  installation_info_assembler.__get_cpu_flags()
  __mock_run_shell_command.assert_called_once_with('lscpu | grep "Flags:"')

@pytest.mark.parametrize(
  "__mock_run_shell_command,expected_cpu_flags",
  [
    pytest.param((0, ""), []),
    pytest.param((1, "flag1 flag2"), []),
    pytest.param((0, "flag1 flag2"), ["flag1", "flag2"])
  ],
  indirect=["__mock_run_shell_command"]
)
def test_returns_expected_cpu_flags(
  __mock_run_shell_command,
  expected_cpu_flags
):
  architecture_name = installation_info_assembler.__get_cpu_flags()
  assert (
    architecture_name == expected_cpu_flags
  ), get_assertion_message("architecture name", expected_cpu_flags, architecture_name)

def test_calls_os_getenv_when_checking_if_is_installed_by_scipion(__mock_os_getenv):
  installation_info_assembler.__is_installed_by_scipion()
  __mock_os_getenv.assert_called_once_with("SCIPION_SOFTWARE")

@pytest.mark.parametrize(
  "__mock_os_getenv,expected_is_installed",
  [
    pytest.param(None, False),
    pytest.param("", False),
    pytest.param("/path/to/scipion", True)
  ],
  indirect=["__mock_os_getenv"]
)
def test_returns_expected_is_installed_by_scipion(
  __mock_os_getenv,
  expected_is_installed
):
  is_installed = installation_info_assembler.__is_installed_by_scipion()
  assert (
    is_installed == expected_is_installed
  ), get_assertion_message("\"is installed by Scipion\" value", expected_is_installed, is_installed)

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

def test_calls_platform_system_when_getting_os_release_name(__mock_platform_system):
  installation_info_assembler.get_os_release_name()
  __mock_platform_system.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_os_is_linux",
  [
    pytest.param(True),
    pytest.param(False)
  ],
  indirect=["__mock_os_is_linux"]
)
def test_calls_or_not_platform_release_according_to_os_when_getting_os_release_name(
  __mock_os_is_linux,
  __mock_platform_system,
  __mock_platform_release,
  __mock_distro_name,
  __mock_distro_version
):
  installation_info_assembler.get_os_release_name()
  if __mock_os_is_linux:
    __mock_platform_release.assert_not_called()
  else:
    __mock_platform_release.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_os_is_linux",
  [
    pytest.param(True),
    pytest.param(False)
  ],
  indirect=["__mock_os_is_linux"]
)
def test_returns_expected_os_release_name(
  __mock_os_is_linux,
  __mock_platform_system,
  __mock_platform_release,
  __mock_distro_name,
  __mock_distro_version
):
  release_name = installation_info_assembler.get_os_release_name()
  expected_release_name = __RELEASE_NAME_LINUX if __mock_os_is_linux else __RELEASE_NAME_WINDOWS
  assert (
    release_name == expected_release_name
  ), get_assertion_message("OS release name", expected_release_name, release_name)

@pytest.mark.parametrize(
  "received_branch_name,expected_branch_name",
  [
    pytest.param(None, versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]),
    pytest.param("", versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]),
    pytest.param(versions.MASTER_BRANCHNAME, versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]),
    pytest.param("devel", "devel")
  ]
)
def test_returns_expected_installation_branch_name(
  received_branch_name,
  expected_branch_name
):
  branch_name = installation_info_assembler.__get_installation_branch_name(
    received_branch_name
  )
  assert (
    branch_name == expected_branch_name
  ), get_assertion_message("installation branch name", expected_branch_name, branch_name)

def test_calls_get_user_id_when_getting_installation_info(__mock_get_user_id):
  __mock_get_user_id.return_value = None
  installation_info_assembler.get_installation_info()
  __mock_get_user_id.assert_called_once_with()

def test_calls_get_library_versions_from_cmake_file_when_getting_installation_info(
  __mock_get_user_id,
  __mock_get_library_versions_from_cmake_file,
  __mock_run_parallel_jobs
):
  installation_info_assembler.get_installation_info()
  __mock_get_library_versions_from_cmake_file.assert_called_once_with(
    constants.LIBRARY_VERSIONS_FILE
  )

def test_calls_get_os_release_name_when_getting_installation_info(
  __mock_get_user_id,
  __mock_get_library_versions_from_cmake_file,
  __mock_run_parallel_jobs,
  __mock_get_os_release_name
):
  installation_info_assembler.get_installation_info()
  __mock_get_os_release_name.assert_called_once_with()

def test_calls_run_parallel_jobs_when_getting_installation_info(
  __mock_get_user_id,
  __mock_get_library_versions_from_cmake_file,
  __mock_run_parallel_jobs
):
  installation_info_assembler.get_installation_info()
  __mock_run_parallel_jobs.assert_called_once_with(
    [
      installation_info_assembler.__get_cpu_flags,
      git_handler.get_current_branch,
      git_handler.is_branch_up_to_date,
      installation_info_assembler.__is_installed_by_scipion,
      installation_info_assembler.__get_log_tail
    ],
    [(), (), (), (), ()]
  )

@pytest.mark.parametrize(
  "ret_code,"
  "__mock_get_user_id,"
  "__mock_get_library_versions_from_cmake_file,"
  "__mock_run_parallel_jobs,"
  "expected_info",
  [
    pytest.param(0, None, {}, [None for _ in range(5)], None),
    pytest.param(1, None, {}, [None for _ in range(5)], None),
    pytest.param(0, None, {"test": "something"}, ["value" for _ in range(5)], None),
    pytest.param(1, None, {"test": "something"}, ["value" for _ in range(5)], None),
    pytest.param(0, None, __LIBRARY_VERSIONS, ["value" for _ in range(5)], None),
    pytest.param(1, None, __LIBRARY_VERSIONS, ["value" for _ in range(5)], None),
    pytest.param(0, __USER_ID, {}, [None for _ in range(5)], __EMPTY_INSTALLATION_INFO),
    pytest.param(1, __USER_ID, {}, [None for _ in range(5)], {**__EMPTY_INSTALLATION_INFO, "returnCode": 1}),
    pytest.param(0, __USER_ID, __LIBRARY_VERSIONS, __ENVIROMENT_INFO, {**__INSTALLATION_INFO, "logTail": None}),
    pytest.param(1, __USER_ID, __LIBRARY_VERSIONS, __ENVIROMENT_INFO, {**__INSTALLATION_INFO, "returnCode": 1})
  ],
  indirect=[
    "__mock_get_user_id",
    "__mock_get_library_versions_from_cmake_file",
    "__mock_run_parallel_jobs"
  ]
)
def test_returns_expected_installation_info(
  ret_code,
  __mock_get_user_id,
  __mock_get_library_versions_from_cmake_file,
  __mock_run_parallel_jobs,
  expected_info,
  __mock_get_os_release_name
):
  installation_info = installation_info_assembler.get_installation_info(ret_code=ret_code)
  assert (
    installation_info == expected_info
  ), get_assertion_message("installation information", expected_info, installation_info)

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

@pytest.fixture(params=[__USER_ID])
def __mock_get_user_id(request):
  with patch(
    "xmipp3_installer.api_client.assembler.installation_info_assembler.__get_user_id"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[__LIBRARY_VERSIONS])
def __mock_get_library_versions_from_cmake_file(request):
  with patch(
    "xmipp3_installer.installer.handlers.cmake.cmake_handler.get_library_versions_from_cmake_file"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[__ENVIROMENT_INFO])
def __mock_run_parallel_jobs(request):
  with patch(
    "xmipp3_installer.installer.orquestrator.run_parallel_jobs"
  ) as mock_method:
    mock_method.side_effect = [request.param]
    yield mock_method

@pytest.fixture(params=[None])
def __mock_os_getenv(request):
  with patch("os.getenv") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture(params=[True])
def __mock_os_is_linux(request):
  return request.param

@pytest.fixture()
def __mock_platform_system(__mock_os_is_linux):
  with patch("platform.system") as mock_method:
    mock_method.return_value = __PLATFORM_SYSTEM_LINUX if __mock_os_is_linux else __PLATFORM_SYSTEM_WINDOWS
    yield mock_method

@pytest.fixture
def __mock_platform_release():
  with patch("platform.release") as mock_method:
    mock_method.return_value = __PLATFORM_RELEASE_WINDOWS
    yield mock_method

@pytest.fixture
def __mock_distro_name():
  with patch("distro.name") as mock_method:
    mock_method.return_value = __DISTRO_NAME
    yield mock_method

@pytest.fixture
def __mock_distro_version():
  with patch("distro.version") as mock_method:
    mock_method.return_value = __DISTRO_VERSION
    yield mock_method

@pytest.fixture
def __mock_get_os_release_name():
  with patch(
    "xmipp3_installer.api_client.assembler.installation_info_assembler.get_os_release_name"
  ) as mock_method:
    mock_method.return_value = __RELEASE_NAME_LINUX
    yield mock_method
