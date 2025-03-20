"""
### Paths Module.

This module defines various paths used throughout the application.
"""

import os

from xmipp3_installer.installer import constants

# General paths
SOURCES_PATH = "src"
BUILD_PATH = "build"
INSTALL_PATH = "dist"
BINARIES_PATH = os.path.join(INSTALL_PATH, "bin")
SCIPION_SOFTWARE_EM = os.path.join("scipionfiles", "downloads", "scipion", "software", "em")

# General file paths
LOG_FILE = 'compilation.log'
LIBRARY_VERSIONS_FILE = os.path.join(BUILD_PATH, 'versions.txt')
CONFIG_FILE = 'xmipp.conf'
VERSION_INFO_FILE = "version-info.json"

# Source paths
def get_source_path(source: str) -> str:
  """
  ### Returns the path to the given source.

  #### Params:
  - source (str): Source name.

  #### Returns:
  - (str): Path to the source.
  """
  return os.path.abspath(os.path.join(SOURCES_PATH, source))
XMIPP_CORE_PATH = get_source_path(constants.XMIPP_CORE)
XMIPP_SOURCE_PATHS = [get_source_path(source) for source in constants.XMIPP_SOURCES]
