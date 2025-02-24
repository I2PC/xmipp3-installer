"""### Contains constants used to configure the installer."""

import os

# Repository names
XMIPP = 'xmipp'
XMIPP_CORE = 'xmippCore'
XMIPP_VIZ = 'xmippViz'
XMIPP_SOURCES = [XMIPP_CORE, XMIPP_VIZ]

# Branch names
DEVEL_BRANCHNAME = 'devel'
MASTER_BRANCHNAME = 'master'

# Paths
BUILD_PATH = "build"
INSTALL_PATH = "dist"
BINARIES_PATH = os.path.join(INSTALL_PATH, "bin")
#BUILD_TYPE = "Release"
#CMAKE_CACHE_PATH = os.path.join(BUILD_PATH, 'CMakeCache.txt')
LOG_FILE = 'compilation.log'
LIBRARY_VERSIONS_FILE = os.path.join(BUILD_PATH, 'versions.txt')
CONFIG_FILE = 'xmipp.conf'
SCIPION_SOFTWARE_EM = os.path.join("scipionfiles", "downloads", "scipion", "software", "em")
VERSION_INFO_FILE = "version-info.json"

# Context
VERSIONS_CONTEXT_KEY = "versions"

# Others
TAIL_LOG_NCHARS = 300
