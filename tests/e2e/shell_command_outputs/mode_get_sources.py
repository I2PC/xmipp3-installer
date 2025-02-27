from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants

from . import XMIPP_DOCS

__GETTING_SOURCES_HEADER = "------------------- Getting Xmipp sources ------------------"
__WORKING_MESSAGE = logger.yellow("Working...")
__DONE_MESSAGE = logger.green("Done")
__CLONING_XMIPP_CORE = f"Cloning {constants.XMIPP_CORE}..."
__CLONING_XMIPP_VIZ = f"Cloning {constants.XMIPP_VIZ}..."

BRANCH_NAME = "branch_name"
def __get_branch_not_found_warning(source_name: str) -> str:
  return logger.yellow("\n".join([
    f"Warning: branch \'{BRANCH_NAME}\' does not exist for repository with url https://github.com/i2pc/{source_name}.",
    "Falling back to repository's default branch."
  ]))

GIT_COMMAND_FAILURE_MESSAGE = "failure message"
__FAILURE_COMPLETE_MESSAGE = logger.red(f"""{GIT_COMMAND_FAILURE_MESSAGE}

Error 2: Error cloning xmipp repository with git.
Please review the internet connection and the git package.
{XMIPP_DOCS}""")

SUCCESS = f"""{__GETTING_SOURCES_HEADER}
{__CLONING_XMIPP_CORE}
{__WORKING_MESSAGE}
{__DONE_MESSAGE}
{__CLONING_XMIPP_VIZ}
{__WORKING_MESSAGE}
{__DONE_MESSAGE}
"""

SUCCESS_WITH_WARNING = f"""{__GETTING_SOURCES_HEADER}
{__CLONING_XMIPP_CORE}
{__WORKING_MESSAGE}
{__get_branch_not_found_warning(constants.XMIPP_CORE)}
{__DONE_MESSAGE}
{__CLONING_XMIPP_VIZ}
{__WORKING_MESSAGE}
{__get_branch_not_found_warning(constants.XMIPP_VIZ)}
{__DONE_MESSAGE}
"""

FAILURE = f"""{__GETTING_SOURCES_HEADER}
{__CLONING_XMIPP_CORE}
{__WORKING_MESSAGE}
{__FAILURE_COMPLETE_MESSAGE}
"""

FAILURE_WITH_WARNING = f"""{__GETTING_SOURCES_HEADER}
{__CLONING_XMIPP_CORE}
{__WORKING_MESSAGE}
{__get_branch_not_found_warning(constants.XMIPP_CORE)}
{__FAILURE_COMPLETE_MESSAGE}
"""
