from xmipp3_installer.application.logger.logger import logger

from . import XMIPP_DOCS

CMAKE_EXECUTABLE = "cmake"

__CONFIGURE_ERROR = logger.red("\n".join([
  "Error 4: Error configuring with CMake.",
  "Check the inside file 'compilation.log'.",
  XMIPP_DOCS
]))

__COMMON_SECTION = f"""------------------ Configuring with CMake ------------------
{CMAKE_EXECUTABLE} -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=False -DCMAKE_CXX_FLAGS=-mtune=native -DCMAKE_C_FLAGS=-mtune=native -DCMAKE_INSTALL_PREFIX=dist -DCMAKE_SKIP_RPATH=True -DXMIPP_LINK_TO_SCIPION=False -DXMIPP_USE_CUDA=False -DXMIPP_USE_MATLAB=False -DXMIPP_USE_MPI=False"""

SUCCESS = f"""{__COMMON_SECTION}
-- Building for: NMake Makefiles
-- Configuring incomplete, errors occurred!
{__CONFIGURE_ERROR}
"""

FAILURE = f"""{__COMMON_SECTION}
-- Building for: NMake Makefiles
-- Configuring incomplete, errors occurred!
{__CONFIGURE_ERROR}
"""
