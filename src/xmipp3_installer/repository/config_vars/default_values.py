"""### Contains the defaukt values for the config variables."""

from xmipp3_installer.repository.config_vars import vars
from xmipp3_installer.installer import disaster_drawer

ON = 'ON'
OFF = 'OFF'
CONFIG_DEFAULT_VALUES = {
	vars.SEND_INSTALLATION_STATISTICS: ON,
	vars.CMAKE: None,
	vars.CUDA: ON,
	vars.MPI: ON,
	vars.CC: None,
	vars.CXX: None,
	vars.CMAKE_INSTALL_PREFIX: INSTALL_PATH,
	vars.CC_FLAGS: vars.TUNE_FLAG,
	vars.CXX_FLAGS: vars.TUNE_FLAG,
	vars.CUDA_COMPILER: None,
	vars.PREFIX_PATH: disaster_drawer.get_conda_prefix_path(),
	vars.MPI_HOME: None,
	vars.PYTHON_HOME: None,
	vars.FFTW_HOME: None,
	vars.TIFF_HOME: None,
	vars.HDF5_HOME: None,
	vars.JPEG_HOME: None,
	vars.SQLITE_HOME: None,
	vars.CUDA_CXX: None,
	vars.MATLAB: ON,
	vars.LINK_SCIPION: ON,
	vars.BUILD_TESTING: ON,
 	vars.SKIP_RPATH: ON
}
