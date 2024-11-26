import os
import tempfile
from unittest.mock import patch, Mock

import pytest

from xmipp3_installer.repository.config import ConfigurationFileHandler
from xmipp3_installer.repository.config_vars import default_values

from .... import get_assertion_message

__DATE = "25-11-2024 01:26.46"
__FILE_LINES = [
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
	f"# {ConfigurationFileHandler._ConfigurationFileHandler__LAST_MODIFIED_TEXT} {__DATE}",
	""
]

def test_writes_default_config_when_there_is_no_config_file(
	__mock_config_file,
	__mock_datetime_strftime
):
	config_handler = ConfigurationFileHandler(__mock_config_file.name)
	config_handler.write_config()
	file_content = ''.join(
		config_handler._ConfigurationFileHandler__get_file_content()
	).split("\n")
	assert (
		file_content == __FILE_LINES
	), get_assertion_message("config file content", __FILE_LINES, file_content)

@pytest.fixture
def __mock_config_file():
	with tempfile.NamedTemporaryFile(
		delete=True,
		delete_on_close=False,
		dir=os.path.dirname(os.path.abspath(__file__))
	) as temp_file:
		try:
			yield temp_file
		finally:
			if os.path.exists(temp_file.name):
				os.remove(temp_file.name)

@pytest.fixture
def __mock_datetime_strftime():
	with patch("xmipp3_installer.repository.config.datetime") as mock_lib:
		mock_today = Mock()
		mock_today.strftime.return_value = __DATE
		mock_lib.today.return_value = mock_today
		yield mock_lib
