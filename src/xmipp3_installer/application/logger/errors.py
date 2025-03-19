"""### Contains all constants needed for handling errors during Xmipp's installation."""

from xmipp3_installer.installer.urls import CMAKE_INSTALL_DOCS_URL
from xmipp3_installer.installer.constants import paths

# Error codes
INTERRUPTED_ERROR = -1
OK = 0
UNKOW_ERROR = 1
SOURCE_CLONE_ERROR = 2
CMAKE_ERROR = 3
CMAKE_CONFIGURE_ERROR = 4
CMAKE_COMPILE_ERROR = 5
CMAKE_INSTALL_ERROR = 6
IO_ERROR = 7

# Error messages
__CHECK_LOG_MESSAGE = f'Check the inside file \'{paths.LOG_FILE}\'.'
ERROR_CODES = {
  INTERRUPTED_ERROR: ['Process was interrupted by the user.', ''],
  UNKOW_ERROR: ['', ''],
  SOURCE_CLONE_ERROR: ['Error cloning xmipp repository with git.', 'Please review the internet connection and the git package.'],
  CMAKE_ERROR: ['There was an error with CMake.', f'Please install it by following the instructions at {CMAKE_INSTALL_DOCS_URL}'],
  CMAKE_CONFIGURE_ERROR: ['Error configuring with CMake.', __CHECK_LOG_MESSAGE],
  CMAKE_COMPILE_ERROR: ['Error compiling with CMake.', __CHECK_LOG_MESSAGE],
  CMAKE_INSTALL_ERROR: ['Error installing with CMake.', __CHECK_LOG_MESSAGE],
  IO_ERROR: ['Input/output error.', 'This error can be caused by the installer not being able to read/write/create/delete a file. Check your permissions on this directory.']
}
