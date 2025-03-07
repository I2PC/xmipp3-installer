import re

from . import (
  CMAKE_EXECUTABLE, VALID_PROJECT,
  get_project_abs_subpath, get_predefined_error
)

EXECUTION_TIME = "X.Y"
BUILD_FILES_WRITTEN_MESSAGE_START = "-- Build files have been written to: "
VALID_PATH = get_project_abs_subpath(VALID_PROJECT, "build")
GENERATOR_LINE = "-- Building for: Ninja\n"

__COMMON_SECTION = f"""------------------ Configuring with CMake ------------------
{CMAKE_EXECUTABLE} -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=False -DCMAKE_CXX_FLAGS=-mtune=native -DCMAKE_C_FLAGS=-mtune=native -DCMAKE_INSTALL_PREFIX=dist -DCMAKE_SKIP_RPATH=True -DXMIPP_LINK_TO_SCIPION=False -DXMIPP_USE_CUDA=False -DXMIPP_USE_MATLAB=False -DXMIPP_USE_MPI=False"""

SUCCESS = f"""{__COMMON_SECTION}
-- Configuring done ({EXECUTION_TIME}s)
-- Generating done ({EXECUTION_TIME}s)
{BUILD_FILES_WRITTEN_MESSAGE_START}{VALID_PATH}
"""

FAILURE = f"""{__COMMON_SECTION}
-- Configuring incomplete, errors occurred!
{get_predefined_error(4, "configuring")}
"""

def normalize_execution_times(raw_output: str) -> str: # Execution times vary from one execution to another
	return re.sub(r'\(\d+\.\ds\)', f"({EXECUTION_TIME}s)", raw_output)
