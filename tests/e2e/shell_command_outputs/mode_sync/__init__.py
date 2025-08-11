import os

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor

from ... import shell_command_outputs

__RELATIVIZED_SYNC_PROGRAM_NAME = os.path.join(".", mode_sync_executor._SYNC_PROGRAM_NAME)
SYNC_PROGRAM_NAME = f"{__RELATIVIZED_SYNC_PROGRAM_NAME}.py"
__NO_PROGRAM_INITIAL_MESSAGE = f"{os.path.join(mode_sync_executor._SYNC_PROGRAM_PATH, SYNC_PROGRAM_NAME)} does not exist."
NO_PROGRAM = f"""{logger.red(__NO_PROGRAM_INITIAL_MESSAGE)}
{logger.red("Xmipp needs to be compiled successfully before running this command!")}
{shell_command_outputs.IO_ERROR}
"""
