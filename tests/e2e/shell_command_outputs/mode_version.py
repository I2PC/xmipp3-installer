from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.installer.handlers import git_handler
from xmipp3_installer.installer.modes.mode_version_executor import ModeVersionExecutor

__TITLE = f"Xmipp {versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]} ({git_handler.get_current_branch()})"

__SOURCE_NOT_FOUND_MESSAGE = logger.yellow("Not found")

__WARNING_MESSAGE = f"""{logger.yellow("This project has not yet been configured, so some detectable dependencies have not been properly detected.")}
{logger.yellow("Run mode 'getSources' and then 'configBuild' to be able to show all detectable ones.")}"""

__LIBRARIES_WITH_VERSIONS = """CMake:                   3.31.3
CC:                      GNU-13.3.0
CXX:                     GNU-13-3-0
Python3:                 3.12.8
MPI:                     3.1
HDF5:                    1.10.10
JPEG:                    80
SQLite3:                 3.45.1
Java:                    17.0.13
"""

__COMMON_SECTION = f"""{logger.bold(__TITLE)}

Release date:            {versions.RELEASE_DATE}
Compilation date:        -
System version:          {installation_info_assembler.get_os_release_name()}"""

__SOURCES_NOT_FOUND_SECTION = f"""xmippCore branch:        {__SOURCE_NOT_FOUND_MESSAGE}
xmippViz branch:         {__SOURCE_NOT_FOUND_MESSAGE}
scipion-em-xmipp branch: {__SOURCE_NOT_FOUND_MESSAGE}"""

FULL_INFO_BEFORE_CONFIG = f"""{__COMMON_SECTION}
{__SOURCES_NOT_FOUND_SECTION}

{__WARNING_MESSAGE}
"""

FULL_INFO_AFTER_CONFIG_NO_SOURCES = f"""{__COMMON_SECTION}
{__SOURCES_NOT_FOUND_SECTION}

{__LIBRARIES_WITH_VERSIONS}
{__WARNING_MESSAGE}
"""
