"""### Contains the defaukt values for the config variables."""

from xmipp3_installer.repository.config_vars import variables
from xmipp3_installer.installer import disaster_drawer

ON = 'ON'
OFF = 'OFF'
CONFIG_DEFAULT_VALUES = {
	variables.SEND_INSTALLATION_STATISTICS: ON,
	variables.CMAKE: None,
	variables.CUDA: ON,
	variables.MPI: ON,
	variables.CC: None,
	variables.CXX: None,
	variables.CMAKE_INSTALL_PREFIX: INSTALL_PATH,
	variables.CC_FLAGS: variables.TUNE_FLAG,
	variables.CXX_FLAGS: variables.TUNE_FLAG,
	variables.CUDA_COMPILER: None,
	variables.PREFIX_PATH: disaster_drawer.get_conda_prefix_path(),
	variables.MPI_HOME: None,
	variables.PYTHON_HOME: None,
	variables.FFTW_HOME: None,
	variables.TIFF_HOME: None,
	variables.HDF5_HOME: None,
	variables.JPEG_HOME: None,
	variables.SQLITE_HOME: None,
	variables.CUDA_CXX: None,
	variables.MATLAB: ON,
	variables.LINK_SCIPION: ON,
	variables.BUILD_TESTING: ON,
 	variables.SKIP_RPATH: ON
}
