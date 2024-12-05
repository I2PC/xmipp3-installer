"""### Containsconstants used to configure the installer."""

import os

# Repository names
#XMIPP = 'xmipp'
#XMIPP_CORE = 'xmippCore'
#XMIPP_VIZ = 'xmippViz'
#XMIPP_PLUGIN = 'scipion-em-xmipp'

# Paths
#SOURCES_PATH = "src"
BUILD_PATH = "build"
INSTALL_PATH = "dist"
#BUILD_TYPE = "Release"
#CMAKE_CACHE_PATH = os.path.join(BUILD_PATH, 'CMakeCache.txt')
LOG_FILE = 'compilation.log'
LIBRARY_VERSIONS_FILE = os.path.join(BUILD_PATH, 'versions.txt')
CONFIG_FILE = 'xmipp.conf'

# Others
TAIL_LOG_NCHARS = 300
