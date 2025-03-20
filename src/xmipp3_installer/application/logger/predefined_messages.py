"""
### Predefined Messages Module.

This module contains functions to generate standard log messages.
"""

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.handlers import git_handler

__SECTION_MESSAGE_LEN = 60

def get_done_message() -> str:
  """
  ### Returns the standard message string to use when a task is completed.

  #### Returns:
  - (str): Task completion message.
  """
  return logger.green("Done")

def get_working_message() -> str:
  """
  ### Returns the standard message string to use when a task is in progress.

  #### Returns:
  - (str): Task in progress message.
  """
  return logger.yellow("Working...")

def get_section_message(text: str) -> str:
  """
  ### Returns the given text as a section header.

  #### Params:
  - text (str): Title of the section.

  #### Returns:
  - (str): Formatted section header.
  """
  minimum_remaining_len = len("-  -")
  text_len = len(text)
  remaining_len = __SECTION_MESSAGE_LEN - text_len
  if remaining_len < minimum_remaining_len:
    return text
  
  n_dashes = remaining_len - 2
  n_final_dashes = int(n_dashes / 2)
  n_initial_dashes = n_dashes - n_final_dashes
  final_dashes = ''.join(['-' for _ in range(n_final_dashes)])
  initial_dashes = ''.join(['-' for _ in range(n_initial_dashes)])
  return f"{initial_dashes} {text} {final_dashes}"

def get_success_message(tag_version: str) -> str:
  """
  ### Returns the message shown when Xmipp is compiled successfully.

  #### Params:
  - tag_version (str): Version number of the latest release.
  
  #### Returms:
  - (str): Success message.
  """
  release_name = tag_version if git_handler.is_tag() else git_handler.get_current_branch()

  box_wrapper = '*  *'
  half_len_box_wrapper = int(len(box_wrapper) / 2)
  release_message = f'Xmipp {release_name} has been successfully installed, enjoy it!'
  total_len = len(release_message) + len(box_wrapper)
  release_message = f'{box_wrapper[:half_len_box_wrapper]}{logger.green(release_message)}{box_wrapper[half_len_box_wrapper:]}'
  margin_line = f"*{' ' * (total_len - 2)}*"
  box_border = '*' * total_len

  return '\n'.join(["", box_border, margin_line, release_message, margin_line, box_border])
