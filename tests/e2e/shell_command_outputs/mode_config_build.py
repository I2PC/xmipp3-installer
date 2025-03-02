from xmipp3_installer.application.logger.logger import logger

from . import XMIPP_DOCS

CMAKE_EXECUTABLE = "cmake"

__CONFIGURE_ERROR = logger.red("\n".join([
  "Error 4: Error configuring with CMake.",
  "Check the inside file 'compilation.log'.",
  XMIPP_DOCS,
  ""
]))

SUCCESS = f"""------------------ Configuring with CMake ------------------
{CMAKE_EXECUTABLE} -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS=-mtune=native -DXMIPP_USE_MATLAB=True -DCMAKE_CXX_FLAGS=-mtune=native -DXMIPP_USE_CUDA=True -DXMIPP_LINK_TO_SCIPION=True -DBUILD_TESTING=True -DXMIPP_USE_MPI=True -DCMAKE_INSTALL_PREFIX=dist -DCMAKE_SKIP_RPATH=True
-- Configuring incomplete, errors occurred!
{__CONFIGURE_ERROR}"""

FAILURE = f"""------------------ Configuring with CMake ------------------
{CMAKE_EXECUTABLE} -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=dist -DCMAKE_CXX_FLAGS=-mtune=native -DXMIPP_USE_MATLAB=True -DXMIPP_USE_CUDA=True -DXMIPP_LINK_TO_SCIPION=True -DBUILD_TESTING=True -DCMAKE_SKIP_RPATH=True -DCMAKE_C_FLAGS=-mtune=native -DXMIPP_USE_MPI=True
-- Building for: NMake Makefiles
-- Configuring incomplete, errors occurred!
{__CONFIGURE_ERROR}"""
