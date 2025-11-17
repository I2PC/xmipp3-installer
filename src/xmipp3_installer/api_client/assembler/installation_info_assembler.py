"""### Contains functions to assemble the data dictionary required by the API client."""

import getpass
import hashlib
import platform
import re
import os
from typing import Optional, List, Dict

import distro

from xmipp3_installer.installer import constants, orquestrator
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler, git_handler, versions_manager
from xmipp3_installer.installer.handlers.cmake import cmake_constants, cmake_handler

def get_installation_info(version_manager: versions_manager.VersionsManager, ret_code: int=0) -> Dict:
  """
  ### Creates a dictionary with the necessary data for the API POST message.
  
  #### Params:
  - version_manager (VersionsManager): Object containing all the version-related info.
  - ret_code (int): Optional. Return code for the API request.
  
  #### Return:
  - (dict): Dictionary with the required info.
  """
  library_versions = cmake_handler.get_library_versions_from_cmake_file(
    paths.LIBRARY_VERSIONS_FILE
  )
  environment_info = orquestrator.run_parallel_jobs(
    [
      __get_cpu_flags,
      git_handler.get_current_branch,
      git_handler.is_branch_up_to_date,
      __is_installed_by_scipion,
      __get_log_tail
    ],
    [(), (), (), (), ()]
  )

  return {
    "user": {
      "userId": __get_user_id()
    },
    "version": {
      "os": get_os_release_name(),
      "cpuFlags": environment_info[0],
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
      "branch": __get_installation_branch_name(
        environment_info[1], version_manager
      ),
      "updated": environment_info[2],
      "installedByScipion": environment_info[3]
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
  platform_system = platform.system()
  if platform_system == "Linux":
    return f"{distro.name()} {distro.version()}"
  return f"{platform_system} {platform.release()}"

def __get_installation_branch_name(branch_name: str, version_manager: versions_manager.VersionsManager) -> str:
  """
  ### Returns the branch or release name of Xmipp.

  #### Params:
  - branch_name (str): Retrieved branch name.
  - version_manager (VersionsManager): Object containing all the version-related info.

  #### Return:
  - (str): Release name if Xmipp is in a release branch, or the branch name otherwise.
  """
  return branch_name if (branch_name and not git_handler.is_tag()) else version_manager.xmipp_version_name

def __get_user_id() -> str:
  """
  ### Returns the unique user id for this machine.
  
  #### Returns:
  - (str): User id, or 'Anoymous' if there were any errors.
  """
  identifier = __get_mac_address()
  if not identifier:
    identifier = getpass.getuser()
    if not identifier:
      return "Anonymous"
  
  sha256 = hashlib.sha256()
  sha256.update(identifier.encode())
  return sha256.hexdigest()

def __get_cpu_flags() -> List[str]:
  """
  ### This function obtains the list of compilation flags supported by the CPU.

  #### Returns:
  - (list(str)): List of flags supported by the CPU.  
  """
  flags_header = "Flags:"
  ret_code, flags_line = shell_handler.run_shell_command(f'lscpu | grep \"{flags_header}\"')
  if ret_code:
    return []
  flags_line = flags_line.replace(flags_header, "").strip()
  return [flag for flag in flags_line.split(" ") if flag]

def __get_log_tail() -> Optional[str]:
  """
  ### Returns the last lines of the installation log.
  
  #### Returns:
  - (str | None): Installation log's last lines, or None if there were any errors.
  """
  ret_code, output = shell_handler.run_shell_command(
    f"tail -n {constants.TAIL_LOG_NCHARS} {paths.LOG_FILE}"
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
    match = re.match(r"^\d+: (enp|wlp|eth|ens|eno)\w+", lines[line_index])
    if not match:
      continue
    mac_match = re.search(r"link/ether ([0-9a-f:]{17})", lines[line_index + 1])
    if mac_match:
      return mac_match.group(1)

def __is_installed_by_scipion() -> bool:
  """
  ### Checks if the current xmipp installation is being carried out from Scipion.

  #### Returns:
  - (bool): True if the installation is executed by Scipion, False otherwise.
  """
  return bool(os.getenv("SCIPION_SOFTWARE"))
