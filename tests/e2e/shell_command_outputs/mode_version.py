from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.handlers import git_handler

from ... import JSON_XMIPP_VERSION_NUMBER, JSON_XMIPP_RELEASE_DATE

__TITLE = f"Xmipp {JSON_XMIPP_VERSION_NUMBER} ({git_handler.get_current_branch()})"
__DATE = "10-12-2024 17:26.33"

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
Java:                    17.0.13"""

__COMMON_SECTION_NO_CONFIG = f"""{logger.bold(__TITLE)}

Release date:            {JSON_XMIPP_RELEASE_DATE}
Compilation date:        -
System version:          {installation_info_assembler.get_os_release_name()}"""

__COMMON_SECTION_WITH_CONFIG = f"""{logger.bold(__TITLE)}

Release date:            {JSON_XMIPP_RELEASE_DATE}
Compilation date:        {__DATE}
System version:          {installation_info_assembler.get_os_release_name()}"""

__SOURCES_NOT_FOUND_SECTION = f"""xmippCore branch:        {__SOURCE_NOT_FOUND_MESSAGE}
xmippViz branch:         {__SOURCE_NOT_FOUND_MESSAGE}"""

def get_sources_found_section():
  found_source_message = f"{git_handler.get_current_branch()} ({git_handler.get_current_commit()})"
  return "\n".join([
    f"xmippCore branch:        {found_source_message}",
    f"xmippViz branch:         {found_source_message}"
  ])

def get_full_info_before_config():
  return '\n'.join([
    __COMMON_SECTION_NO_CONFIG,
    __SOURCES_NOT_FOUND_SECTION,
    "",
    __WARNING_MESSAGE,
    ""
  ])

def get_full_info_before_config_with_sources():
  return '\n'.join([
    __COMMON_SECTION_NO_CONFIG,
    get_sources_found_section(),
    "",
    __WARNING_MESSAGE,
    ""
  ])

def get_full_info_after_config_without_sources():
  return '\n'.join([
    __COMMON_SECTION_WITH_CONFIG,
    __SOURCES_NOT_FOUND_SECTION,
    "",
    __LIBRARIES_WITH_VERSIONS,
    "",
    __WARNING_MESSAGE,
    ""
  ])

def get_full_info_after_config_with_sources():
  return '\n'.join([
    __COMMON_SECTION_WITH_CONFIG,
    get_sources_found_section(),
    "",
    __LIBRARIES_WITH_VERSIONS,
    ""
  ])
