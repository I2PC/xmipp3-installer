from xmipp3_installer.repository.config_vars import default_values
from xmipp3_installer.repository.config import ConfigurationFileHandler

DATE = "25-11-2024 01:26.46"

DEFAULT_FILE_LINES = [
	"##### TOGGLE SECTION #####",
	f"# Activate or deactivate this features using values {default_values.ON}/{default_values.OFF}",
	"SEND_INSTALLATION_STATISTICS=ON",
	"XMIPP_USE_CUDA=ON",
	"XMIPP_USE_MPI=ON",
	"XMIPP_USE_MATLAB=ON",
	"XMIPP_LINK_TO_SCIPION=ON",
	"BUILD_TESTING=ON",
	"CMAKE_SKIP_RPATH=ON",
	"",
	"##### PACKAGE HOME SECTION #####",
	"# Use this variables to use custom installation paths for the required packages.",
	"# If left empty, CMake will search for those packages within your system.",
	"CMAKE=",
	"CMAKE_C_COMPILER=",
	"CMAKE_CXX_COMPILER=",
	"CMAKE_INSTALL_PREFIX=dist",
	"CMAKE_PREFIX_PATH=",
	"MPI_HOME=",
	"CMAKE_CUDA_COMPILER=",
	"Python3_ROOT_DIR=",
	"FFTW_ROOT=",
	"TIFF_ROOT=",
	"HDF5_ROOT=",
	"JPEG_ROOT=",
	"SQLite_ROOT=",
	"CMAKE_CUDA_HOST_COMPILER=",
	"",
	"##### COMPILATION FLAGS #####",
	"# We recommend not modifying this variables unless you know what you are doing.",
	"CMAKE_C_FLAGS=-mtune=native",
	"CMAKE_CXX_FLAGS=-mtune=native",
	"",
	f"# {ConfigurationFileHandler._ConfigurationFileHandler__LAST_MODIFIED_TEXT} {DATE}",
	""
]