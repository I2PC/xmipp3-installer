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

def get_git_command_no_xmipp_no_xmipp_core():
  return '\n'.join([
    __INITIAL_MESSAGE,
    "",
    __get_non_existing_source_message(constants.XMIPP),
    "",
    __get_non_existing_source_message(constants.XMIPP_CORE),
    ""
  ])

def get_git_command_no_xmipp_with_xmipp_core():
  return '\n'.join([
    __INITIAL_MESSAGE,
    "",
    __get_non_existing_source_message(constants.XMIPP),
    "",
    __get_existing_source_message(constants.XMIPP_CORE),
    ""
  ])

def get_git_command_with_xmipp_no_xmipp_core():
  return '\n'.join([
    __INITIAL_MESSAGE,
    "",
    __get_existing_source_message(constants.XMIPP),
    "",
    __get_non_existing_source_message(constants.XMIPP_CORE),
    ""
  ])

def get_git_command_with_xmipp_with_xmipp_core():
  return '\n'.join([
    __INITIAL_MESSAGE,
    "",
    __get_existing_source_message(constants.XMIPP),
    "",
    __get_existing_source_message(constants.XMIPP_CORE),
    ""
  ])
