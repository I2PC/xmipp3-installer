import hashlib
import re
from typing import Optional, List, Dict

from xmipp3_installer.installer import constants
from xmipp3_installer.installer.handlers import shell_handler, git_handler
from xmipp3_installer.installer.handlers.cmake import cmake_constants

def get_installation_info(ret_code: int=0) -> Optional[Dict]:
	"""
	### Creates a JSON with the necessary data for the API POST message.
	
	#### Params:
	- ret_code (int): Optional. Return code for the API request.
	
	#### Return:
	- (dict | None): JSON with the required info or None if user id could not be produced.
	"""
	# Getting user id and checking if it exists
	user_id = __get_user_id()
	if user_id is None:
		return
	
	# Obtaining variables in parallel
	data = parseCmakeVersions(VERSION_FILE)
	json_data = shell_handler.run_shell_command_in_streaming(
		[getOSReleaseName, __get_architecture_name, git_handler.get_current_branch, git_handler.is_branch_up_to_date, __get_log_tail],
		[(), (), (), (), ()]
	)

	# If branch is master or there is none, get release name
	branch_name = XMIPP_VERSIONS[XMIPP][VERSION_KEY] if not json_data[2] or json_data[2] == MASTER_BRANCHNAME else json_data[2]

	# Introducing data into a dictionary
	return {
		"user": {
			"userId": user_id
		},
		"version": {
			"os": json_data[0],
			"architecture": json_data[1],
			"cuda": data.get(cmake_constants.CMAKE_CUDA),
			"cmake": data.get(cmake_constants.CMAKE_CMAKE),
			"gcc": data.get(cmake_constants.CMAKE_GCC),
			"gpp": data.get(cmake_constants.CMAKE_GPP),
			"mpi": data.get(cmake_constants.CMAKE_MPI),
			"python": data.get(cmake_constants.CMAKE_PYTHON),
			"sqlite": data.get(cmake_constants.CMAKE_SQLITE),
			"java": data.get(cmake_constants.CMAKE_JAVA),
			"hdf5": data.get(cmake_constants.CMAKE_HDF5),
			"jpeg": data.get(cmake_constants.CMAKE_JPEG)
		},
		"xmipp": {
			"branch": branch_name,
			"updated": json_data[3]
		},
		"returnCode": ret_code,
		"logTail": json_data[4] if ret_code else None # Only needs log tail if something went wrong
	}

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
	mac_regex = r"link/ether ([0-9a-f:]{17})"
	interface_regex = r"^\d+: (enp|wlp|eth)\w+"
	for line in lines:
		match = re.match(interface_regex, line)
		if not match:
			continue
		interface_name = match.group(1)
		if interface_name.startswith(('enp', 'wlp', 'eth')):
			return re.search(mac_regex, lines[lines.index(line) + 1]).group(1)
	return None
