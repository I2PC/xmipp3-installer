"""### Functions that interact with CMake."""

import shutil
from typing import Dict, Any

from xmipp3_installer.installer.handlers.cmake import cmake_constants
from xmipp3_installer.repository.config_vars import variables

def get_cmake_path(config: Dict[str, Any]) -> str:
	"""
	### Retrieves information about the CMake package and updates the dictionary accordingly.

	#### Params:
	- packages (dict): Dictionary containing package information.

	#### Returns:
	- (dict): Param 'packages' with the 'CMAKE' key updated based on the availability of 'cmake'.
	"""
	return config.get(variables.CMAKE) or shutil.which(cmake_constants.DEFAULT_CMAKE)

def get_cmake_vars_str(config: Dict[str, Any]) -> str:
	"""
	### Converts the variables in the config dictionary into a list as CMake args.
	
	#### Params:
	- config (dict): Dictionary to obtain the parameters from.
	"""
	result = []
	for (key, value) in config.items():
		if key not in variables.INTERNAL_LOGIC_VARS and bool(value):
			result.append(f"-D{key}={value}")
	return ' '.join(result)

def get_library_versions_from_cmake_file(path: str) -> Dict[str, Any]:
	"""
	### Obtains the library versions from the CMake cache file.

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
