from xmipp3_installer.application.logger import predefined_messages

from . import mode_cmake
from .mode_cmake import mode_config_build, mode_compile_and_install

def __get_build_project_subpath(project_name: str) -> str:
  return mode_cmake.get_project_abs_subpath(
    project_name,
    "build"
  )
__COMMON_SECTION = f"""------------------- Managing config file -------------------
Reading config file...
{predefined_messages.get_done_message()}

------------------- Getting Xmipp sources ------------------
Cloning xmippCore...
{predefined_messages.get_working_message()}
{predefined_messages.get_done_message()}
Cloning xmippViz...
{predefined_messages.get_working_message()}
{predefined_messages.get_done_message()}
"""

__COMMON_CONFIG_SUCCESS = "\n".join(
  mode_config_build.SUCCESS.splitlines()[:-2]
)
__CONFIG_SUCCESS_BUILD_FAILURE = f"""{__COMMON_CONFIG_SUCCESS}
{mode_config_build.BUILD_FILES_WRITTEN_MESSAGE_START}{__get_build_project_subpath(mode_cmake.BUILD_ERROR_PROJECT)}
{predefined_messages.get_done_message()}
"""
__CONFIG_SUCCESS_INSTALL_FAILURE = f"""{__COMMON_CONFIG_SUCCESS}
{mode_config_build.BUILD_FILES_WRITTEN_MESSAGE_START}{__get_build_project_subpath(mode_cmake.INSTALL_ERROR_PROJECT)}
{predefined_messages.get_done_message()}
"""

__CONFIG_SUCCESS = f"""{__COMMON_CONFIG_SUCCESS}
{mode_config_build.BUILD_FILES_WRITTEN_MESSAGE_START}{__get_build_project_subpath(mode_cmake.VALID_PROJECT)}
{predefined_messages.get_done_message()}
"""

CONFIG_BUILD_FAILURE = f"""{__COMMON_SECTION}
{mode_config_build.FAILURE}"""

BUILD_FAILURE = f"""{__COMMON_SECTION}
{__CONFIG_SUCCESS_BUILD_FAILURE}
{mode_compile_and_install.BUILD_FAILURE}"""

INSTALL_FAILURE = f"""{__COMMON_SECTION}
{__CONFIG_SUCCESS_INSTALL_FAILURE}
{mode_compile_and_install.INSTALL_FAILURE}"""

SUCCESS = f"""{__COMMON_SECTION}
{__CONFIG_SUCCESS}
{mode_compile_and_install.SUCCESS}"""
