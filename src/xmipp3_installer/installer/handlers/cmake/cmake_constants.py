"""### Contains all needed CMake constants."""

from xmipp3_installer.repository.config_vars import variables

DEFAULT_CMAKE = 'cmake'

# CMake cache file variables to look for
XMIPP_USE_CUDA=variables.CUDA
XMIPP_USE_MPI=variables.MPI
XMIPP_USE_MATLAB=variables.MATLAB
XMIPP_LINK_TO_SCIPION=variables.LINK_SCIPION
CMAKE_BUILD_TYPE='CMAKE_BUILD_TYPE'
CMAKE_C_COMPILER=variables.CC
CMAKE_CXX_COMPILER=variables.CXX
CMAKE_CUDA_COMPILER=variables.CUDA_COMPILER

# CMake saved version variables
CMAKE_PYTHON = 'Python3'
CMAKE_CUDA = 'CUDA'
CMAKE_MPI = 'MPI'
CMAKE_HDF5 = 'HDF5'
CMAKE_JPEG = 'JPEG'
CMAKE_SQLITE = 'SQLite3'
CMAKE_JAVA = 'Java'
CMAKE_CMAKE = 'CMake'
CMAKE_GCC = 'CC'
CMAKE_GPP = 'CXX'
