"""### Functions that interact with CMake."""

import shutil
from typing import Dict, Any, List

from xmipp3_installer.installer.handlers import shell_handler

def get_cmake_path(config: Dict[str, Any]) -> str:
	"""
	### Retrieves information about the CMake package and updates the dictionary accordingly.

	#### Params:
	- packages (dict): Dictionary containing package information.

	#### Returns:
	- (dict): Param 'packages' with the 'CMAKE' key updated based on the availability of 'cmake'.
	"""
	return config.get(CMAKE) or shutil.which(DEFAULT_CMAKE)

def getCMakeVars(config: Dict) -> List[str]:
	"""
	### Converts the variables in the config dictionary into a list as CMake args.
	
	#### Params:
	- configDict (dict): Dictionary to obtain the parameters from.
	"""
	result = []
	for (key, value) in config.items():
		if key not in INTERNAL_LOGIC_VARS and bool(value):
			result.append(f"-D{key}={value}")
	return result

def getCMakeVarsStr(config: Dict) -> str:
	"""
	### Converts the variables in the config dictionary into a string as CMake args.
	
	#### Params:
	- configDict (dict): Dictionary to obtain the parameters from.
	"""
	return ' '.join(getCMakeVars(config))

def checkPackage(package: str, config: Dict[str, Any]) -> bool:
	cmake = get_cmake_path(config)
	args = []
	args.append(f'-DNAME={package}')
	args.append('-DCOMPILER_ID=GNU')
	args.append('-DLANGUAGE=C')
	args.append('-DMODE=EXIST')
	args += getCMakeVars(config)
	
	cmd = cmake + ' ' + ' '.join(args)
	ret_code = shell_handler.run_shell_command(cmd)[0]
	return ret_code == 0

def get_library_versions_from_cmake_file(path: str) -> Dict[str, Any]:
	"""
	### Obtains the library versions from the file compiled by CMake.

	#### Params:
	- path (str): Path to the file containing all versions.

	#### Returns:
	- (dict(str, any)): Dictionary containing all the library versions in the file.
	"""
	result = {}
	with open(path, 'r') as versions_file:
		for line in versions_file.readlines():
			result.update(__get_library_version_from_line(line))
	return result

def __get_library_version_from_line(version_line: str) -> Dict[str, Any]:
	"""
	### Retrieves the name and version of the library in the given line.
	
	#### Params:
	- version_line (str): Text line containing the name and version of the library.
	
	#### Returns:
	- (dict(str, any)): Dictionary where the key is the name and the value is the version.
	"""
	library_with_version = {}
	if version_line:
		name_and_version = version_line.replace("\n", "").split('=')
		version = name_and_version[1] if name_and_version[1] else None
		library_with_version[name_and_version[0]] = version
	return library_with_version
