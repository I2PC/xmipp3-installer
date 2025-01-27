"""### Containsconstants used to configure the installer."""

import os

# Repository names
#XMIPP = 'xmipp'
XMIPP_CORE = 'xmippCore'
XMIPP_VIZ = 'xmippViz'
XMIPP_PLUGIN = 'scipion-em-xmipp'
XMIPP_SOURCES = [XMIPP_CORE, XMIPP_VIZ, XMIPP_PLUGIN]

# Paths
SOURCES_PATH = "src"
BUILD_PATH = "build"
INSTALL_PATH = "dist"
#BUILD_TYPE = "Release"
#CMAKE_CACHE_PATH = os.path.join(BUILD_PATH, 'CMakeCache.txt')
LOG_FILE = 'compilation.log'
LIBRARY_VERSIONS_FILE = os.path.join(BUILD_PATH, 'versions.txt')
CONFIG_FILE = 'xmipp.conf'
SCIPION_SOFTWARE_EM = "scipionfiles/downloads/scipion/software/em"

# Others
TAIL_LOG_NCHARS = 300
