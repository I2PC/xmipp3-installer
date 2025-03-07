from xmipp3_installer.application.logger.logger import logger

from .mode_cmake import mode_config_build, mode_compile_and_install

__WORKING_MESSAGE = logger.yellow("Working...")
__DONE_MESSAGE = logger.green("Done")

__COMMON_SECTION = f"""------------------- Managing config file -------------------
Reading config file...
{__DONE_MESSAGE}

------------------- Getting Xmipp sources ------------------
Cloning xmippCore...
{__WORKING_MESSAGE}
{__DONE_MESSAGE}
Cloning xmippViz...
{__WORKING_MESSAGE}
{__DONE_MESSAGE}
"""

CONFIG_BUILD_FAILURE = f"""{__COMMON_SECTION}
{mode_config_build.FAILURE}"""

BUILD_FAILURE = f"""{__COMMON_SECTION}
{mode_config_build.SUCCESS}
{mode_compile_and_install.BUILD_FAILURE}"""


