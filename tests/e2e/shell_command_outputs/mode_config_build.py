import os

from xmipp3_installer.application.logger.logger import logger

from . import XMIPP_DOCS
from .. import get_cmake_project_path

CMAKE_EXECUTABLE = "cmake"
EXECUTION_TIME = "X.Y"
BUILD_FILES_WRITTEN_MESSAGE_START = "-- Build files have been written to: "
VALID_PATH = os.path.abspath(get_cmake_project_path(os.path.join("valid", "build")))
GENERATOR_LINE = "-- Building for: Ninja\n"

__CONFIGURE_ERROR = logger.red("\n".join([
  "Error 4: Error configuring with CMake.",
  "Check the inside file 'compilation.log'.",
  XMIPP_DOCS
]))

__COMMON_SECTION = f"""------------------ Configuring with CMake ------------------
{CMAKE_EXECUTABLE} -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=False -DCMAKE_CXX_FLAGS=-mtune=native -DCMAKE_C_FLAGS=-mtune=native -DCMAKE_INSTALL_PREFIX=dist -DCMAKE_SKIP_RPATH=True -DXMIPP_LINK_TO_SCIPION=False -DXMIPP_USE_CUDA=False -DXMIPP_USE_MATLAB=False -DXMIPP_USE_MPI=False"""

SUCCESS = f"""{__COMMON_SECTION}
-- Configuring done ({EXECUTION_TIME}s)
-- Generating done ({EXECUTION_TIME}s)
{BUILD_FILES_WRITTEN_MESSAGE_START}{VALID_PATH}
"""

FAILURE = f"""{__COMMON_SECTION}
-- Configuring incomplete, errors occurred!
{__CONFIGURE_ERROR}
"""
