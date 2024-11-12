import hashlib
import re
from typing import Optional, List, Dict

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.handlers import shell_handler, git_handler
from xmipp3_installer.installer.handlers.cmake import cmake_constants, cmake_handler
from xmipp3_installer.installer.tmp import disaster_drawer, versions

def get_installation_info(ret_code: int=0) -> Optional[Dict]:
	"""
	### Creates a dictionary with the necessary data for the API POST message.
	
	#### Params:
	- ret_code (int): Optional. Return code for the API request.
	
	#### Return:
	- (dict | None): Dictionary with the required info or None if user id could not be produced.
	"""
	user_id = __get_user_id()
	if user_id is None:
		return
	
	library_versions = cmake_handler.get_library_versions_from_cmake_file(
		constants.LIBRARY_VERSIONS_FILE
	)
	environment_info = disaster_drawer.run_parallel_jobs(
		[
			get_os_release_name,
			__get_architecture_name,
			git_handler.get_current_branch,
			git_handler.is_branch_up_to_date,
			__get_log_tail
		],
		[(), (), (), (), ()]
	)

	return {
		"user": {
			"userId": user_id
		},
		"version": {
			"os": environment_info[0],
			"architecture": environment_info[1],
			"cuda": library_versions.get(cmake_constants.CMAKE_CUDA),
			"cmake": library_versions.get(cmake_constants.CMAKE_CMAKE),
			"gcc": library_versions.get(cmake_constants.CMAKE_GCC),
			"gpp": library_versions.get(cmake_constants.CMAKE_GPP),
			"mpi": library_versions.get(cmake_constants.CMAKE_MPI),
			"python": library_versions.get(cmake_constants.CMAKE_PYTHON),
			"sqlite": library_versions.get(cmake_constants.CMAKE_SQLITE),
			"java": library_versions.get(cmake_constants.CMAKE_JAVA),
			"hdf5": library_versions.get(cmake_constants.CMAKE_HDF5),
			"jpeg": library_versions.get(cmake_constants.CMAKE_JPEG)
		},
		"xmipp": {
			"branch": __get_installation_branch_name(environment_info[2]),
			"updated": environment_info[3]
		},
		"returnCode": ret_code,
		"logTail": environment_info[4] if ret_code else None # Only needed if something went wrong
	}

def get_os_release_name() -> str:
	"""
	### Returns the name of the current system OS release.

	#### Returns:
	- (str): OS release name.
	"""
	ret_code, os_release_info = shell_handler.run_shell_command('cat /etc/os-release')
	if ret_code:
		return constants.UNKNOWN_VALUE
	
	search = re.search(r'PRETTY_NAME="(.*)"\n', os_release_info)
	return search.group(1) if search else constants.UNKNOWN_VALUE

def __get_installation_branch_name(branch_name: str) -> str:
	"""
	### Returns the branch or release name of Xmipp.

	#### Params:
	- branch_name (str): Retrieved branch name.

	#### Return:
	- (str): Release name if Xmipp is in a release branch, or the branch name otherwise.
	"""
	if not branch_name or branch_name == versions.MASTER_BRANCHNAME:
		return versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]
	else:
		return branch_name

def __get_user_id() -> Optional[str]:
	"""
	### Returns the unique user id for this machine.
	
	#### Returns:
	- (str | None): User id, or None if there were any errors.
	"""
	mac_address = __get_mac_address()
	if not mac_address:
		return
	
	sha256 = hashlib.sha256()
	sha256.update(mac_address.encode())
	return sha256.hexdigest()

def __get_architecture_name() -> str:
	"""
	### Returns the name of the system's architecture name.

	#### Returns:
	- (str): Architecture name.
	"""
	ret_code, architecture = shell_handler.run_shell_command(
		'cat /sys/devices/cpu/caps/pmu_name'
	)
	return constants.UNKNOWN_VALUE if ret_code != 0 or not architecture else architecture

def __get_log_tail() -> Optional[str]:
	"""
	### Returns the last lines of the installation log.
	
	#### Returns:
	- (str | None): Installation log's last lines, or None if there were any errors.
	"""
	ret_code, output = shell_handler.run_shell_command(
		f"tail -n {constants.TAIL_LOG_NCHARS} {constants.LOG_FILE}"
	)
	return output if ret_code == 0 else None

def __get_mac_address() -> Optional[str]:
	"""
	### Returns a physical MAC address for this machine. It prioritizes ethernet over wireless.
	
	#### Returns:
	- (str | None): MAC address, or None if there were any errors.
	"""
	ret_code, output = shell_handler.run_shell_command("ip addr")
	return __find_mac_address_in_lines(output.split('\n')) if ret_code == 0 else None

def __find_mac_address_in_lines(lines: List[str]) -> Optional[str]:
	"""
	### Returns a physical MAC address within the text lines provided.

	#### Params:
	- lines (list(str)): Lines of text where MAC address should be looked for.
	
	#### Returns:
	- (str | None): MAC address if found, None otherwise.
	"""
	for line_index in range(len(lines) - 1):
		line = lines[line_index]
		match = re.match(r"^\d+: (enp|wlp|eth)\w+", line)
		if not match:
			continue
		interface_name = match.group(1)
		if interface_name.startswith(('enp', 'wlp', 'eth')):
			return re.search(
				r"link/ether ([0-9a-f:]{17})",
				lines[line_index + 1]
			).group(1)
	return None
