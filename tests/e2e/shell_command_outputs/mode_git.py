import os

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler

__INITIAL_MESSAGE = "Running command 'git branch' for all xmipp sources..."
__GIT_COMMAND_OUTPUT = shell_handler.run_shell_command("git branch")[1]

def __get_abs_source_path(source_name):
  return os.path.abspath(paths.get_source_path(source_name))

def __get_non_existing_source_message(source_name):
  return logger.yellow(
    f"WARNING: Source {source_name} does not exist in path {__get_abs_source_path(source_name)}. Skipping."
  )

def __get_existing_source_message(source_name):
  return '\n'.join([
    logger.blue(
      f"Running command for {source_name} in path {__get_abs_source_path(source_name)}..."
    ),
    __GIT_COMMAND_OUTPUT
  ])

def get_git_command(exists_xmipp: bool, exists_xmippcore:bool, exists_xmippviz: bool):
  message_lines = [
    __INITIAL_MESSAGE,
    ""
  ]
  for exists, source in [
    (exists_xmipp, constants.XMIPP),
    (exists_xmippcore, constants.XMIPP_CORE),
    (exists_xmippviz, constants.XMIPP_VIZ)
  ]:
    if exists:
      message_lines.append(__get_existing_source_message(source))
    else:
      message_lines.append(__get_non_existing_source_message(source))
    message_lines.append("")

  return "\n".join(message_lines)
