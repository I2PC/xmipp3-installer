import os

from .... import get_test_file

CMAKE_EXECUTABLE = "cmake"
TEST_CONFIG_FILE_PATH = get_test_file(os.path.join("conf-files", "input", "all-off.conf"))
VALID_PROJECT = "valid"
CONFIG_ERROR_PROJECT = "config_error"
BUILD_ERROR_PROJECT = "build_error"
INSTALL_ERROR_PROJECT = "install_error"
