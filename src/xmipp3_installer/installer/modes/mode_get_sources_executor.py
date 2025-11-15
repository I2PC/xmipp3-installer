"""
### Mode Get Sources Executor Module.

This module contains the class to clone or update Xmipp source repositories.
"""

import os
from typing import Dict, Tuple, Optional

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import predefined_messages, errors
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.handlers import git_handler, versions_manager, shell_handler

class ModeGetSourcesExecutor(mode_executor.ModeExecutor):
  """
  ### Mode Get Sources Executor.

  Clones or updates Xmipp source repositories.
  """

  def __init__(self, context: Dict):
    """
    ### Constructor.
    
    #### Params:
    - context (dict): Dictionary containing the installation context variables.
    - substitute (bool): Optional. If True, printed text will be substituted with the next message.
    """
    super().__init__(context)
    self.substitute = not context[params.PARAM_KEEP_OUTPUT]
    self.target_branch = context.pop(params.PARAM_BRANCH)
    versions: versions_manager.VersionsManager = context[constants.VERSIONS_CONTEXT_KEY]
    self.xmipp_tag_name = versions.xmipp_version_name
    self.source_versions: Dict = versions.sources_versions
  
  def run(self) -> Tuple[int, str]:
    """
    ### Clones or updates Xmipp source repositories.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
    """
    logger(predefined_messages.get_section_message("Getting Xmipp sources"))
    for source in constants.XMIPP_SOURCES:
      ret_code, output = self.__get_source(source)
      if ret_code:
        return errors.SOURCE_CLONE_ERROR, output
    return 0, ""
  
  def _set_executor_config(self):
    """### Sets the specific executor params for this mode."""
    super()._set_executor_config()
    self.prints_with_substitution = True
  
  def __select_ref_to_clone(self, source_name: str, source_repo: str) -> Optional[str]:
    """
    ### Selects the reference to clone from the source.

    #### Params:
    - source_name (str): Name of the source to clone.
    - source_repo (str): URL of the source's repository.

    #### Returns:
    - (str | None): The reference name to clone or None if no suitable ref was found.
    """
    current_branch = git_handler.get_current_branch()
    tag_name = None
    if (not current_branch or current_branch == self.xmipp_tag_name):
      tag_name = self.source_versions.get(source_name)
    return git_handler.get_clonable_branch(source_repo, self.target_branch, tag_name)
  
  def __get_source(self, source_name: str) -> Tuple[int, str]:
    """
    ### Gets the given source.
    
    It is cloned if it does not already exist locally.

    #### Params:
    - source_name (str): Name of the source to clone.

    #### Returns:
    - (tuple(int, str)): Tuple containing the return code and the text output produced by the command.
    """
    repo_url = f"{urls.I2PC_REPOSITORY_URL}{source_name}"
    logger(f"Cloning {source_name}...", substitute=self.substitute)
    logger(predefined_messages.get_working_message(), substitute=self.substitute)

    clone_branch = self.__select_ref_to_clone(source_name, repo_url)
    if self.target_branch and not clone_branch:
      warning_message = "\n".join([
        logger.yellow(f"Warning: branch \'{self.target_branch}\' does not exist for repository with url {repo_url}"),
        logger.yellow("Falling back to repository's default branch.")
      ])
      logger(warning_message, substitute=self.substitute)
    
    ret_code, output = _run_source_command(source_name, repo_url, clone_branch)
    if not ret_code:
      logger(predefined_messages.get_done_message(), substitute=self.substitute)
    return ret_code, output

def _run_source_command(source_name: str, source_repo: str, target_branch: Optional[str]) -> Tuple[int, str]:
  """
  ### Executes git clone/checkout commands for a source repository.
  
  If the source already exists locally:
  - If target_branch is specified, checks out that branch.
  - If no target_branch, returns success without changes.
  
  If the source doesn't exist:
  - Clones the repository with the specified branch.
  - If no branch specified, clones with default branch.

  #### Params:
  - source_name (str): Name of the source repository.
  - source_repo (str): URL of the git repository to clone from.
  - target_branch (str | None): Branch or tag to checkout/clone.

  #### Returns:
  - (tuple(int, str)): Tuple containing the return code and the text output produced by the command.
  """
  source_path = paths.get_source_path(source_name)
  if os.path.exists(source_path):
    if not target_branch:
      return 0, ""
    return shell_handler.run_shell_command(
      f"git checkout {target_branch}",
      cwd=source_path
    )
  
  branch_str = (
    f"{params.PARAMS[params.PARAM_BRANCH][params.LONG_VERSION]} {target_branch}"
    if target_branch else ""
  )
  return shell_handler.run_shell_command(f"git clone{branch_str} {source_repo}.git", cwd=paths.SOURCES_PATH)
