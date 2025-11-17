"""### Functions that interact with Git via shell."""

import os
from typing import Optional, Tuple

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.handlers import shell_handler

def get_current_branch(dir: str='./') -> str:
  """
  ### Returns the current branch of the repository of the given directory or empty string if it is not a repository or a recognizable tag.
  
  #### Params:
  - dir (str): Optional. Directory of the repository to get current branch from. Default is current directory.
  
  #### Returns:
  - (str): The name of the branch, 'HEAD' if it is a tag, or empty string if the given directory is not a repository or a recognizable tag.
  """
  ret_code, branch_name = shell_handler.run_shell_command("git rev-parse --abbrev-ref HEAD", cwd=dir)
  # If there was an error, we are in no branch
  return '' if ret_code else branch_name

def is_tag(dir: str='./') -> bool:
  """
  ### Returns True if the current Xmipp repository is in a tag.
  
  This happens when the current commit matches a tag.

  #### Params:
  - dir (str): Optional. Directory of the repository where the check will happen. Default is current directory.
  
  #### Returns:
  - (bool): True if the repository is a tag. False otherwise.
  """
  ret_code, _ = shell_handler.run_shell_command("git describe --tags --exact-match HEAD", cwd=dir)
  return not ret_code

def is_branch_up_to_date(dir: str='./') -> bool:
  """
  ### Returns True if the current branch is up to date, or False otherwise or if some error happened.
  
  #### Params:
  - dir (str): Optional. Directory of the repository to get current branch from. Default is current directory.
  
  #### Returns:
  - (bool): True if the current branch is up to date, or False otherwise or if some error happened.
  """
  current_branch = get_current_branch(dir=dir)
  if not current_branch:
    return False
  
  ret_code = shell_handler.run_shell_command("git fetch", cwd=dir)[0]
  if ret_code != 0:
    return False

  latest_local_commit = shell_handler.run_shell_command(f"git rev-parse {current_branch}", cwd=dir)[1]
  ret_code, latest_remote_commit = shell_handler.run_shell_command(f"git rev-parse origin/{current_branch}")
  if ret_code != 0:
    return False
  
  return latest_local_commit == latest_remote_commit

def get_current_commit(dir: str="./") -> str:
  """
  ### Returns the current commit short hash of a given repository.

  #### Params:
  - dir (str): Optional. Directory of repository.

  #### Returns:
  - (str): Current commit short hash, or empty string if it is not a repo or there were errors.
  """
  ret_code, output = shell_handler.run_shell_command("git rev-parse --short HEAD", cwd=dir)
  if ret_code or not output:
    return ''
  return output

def get_commit_branch(commit: str, dir: str="./") -> str:
  """
  ### Returns the name of the commit branch. It can be a branch name or a release name.

  #### Params:
  - commit (str): Commit hash.
  - dir (str): Optional. Directory to repository.

  #### Returns:
  - (str): Name of the commit branch or release.
  """
  ret_code, output = shell_handler.run_shell_command(f"git name-rev {commit}", cwd=dir)
  if ret_code or not output:
    return ''
  return output.replace(commit, "").replace(" ", "")

def branch_exists_in_repo(repo_url: str, branch: str) -> bool:
  """
  ### Checks if the given branch exists in the given repository.

  #### Params:
  - repo (str): Repository to check from.
  - branch (str): Name of the branch to check for.

  #### Returns:
  - (bool): True if the branch exists, False otherwise.
  """
  return __ref_exists_in_repo(repo_url, branch, True)

def tag_exists_in_repo(repo_url: str, tag: str) -> bool:
  """
  ### Checks if the given tag exists in the given repository.

  #### Params:
  - repo_url (str): Repository to check from.
  - tag (str): Name of the tag to check for.

  #### Returns:
  - (bool): True if the tag exists, False otherwise.
  """
  return __ref_exists_in_repo(repo_url, tag, False)

def get_clonable_branch(repo_url: str, preferred_branch: str, viable_tag: Optional[str]) -> Optional[str]:
  """
  ### Decides the target to be cloned from a given repository.

  The preferred branch will be selected if exists,
  followed in priority by the viable tag if provided.
  Finally, if no branch could be selected, None is returned,
  meaning that repository's default branch will be used.

  #### Params:
  - repo_url (str): Url of the repositori to be cloned.
  - preferred_branch (str): Preferred branch to clone into.
  - viable_tag (str | None): If exists, it is returned if branch does not.

  #### Returns:
  - (str | None): Name of the branch to clone the repository into, or None if not found.
  """
  if preferred_branch and branch_exists_in_repo(repo_url, preferred_branch):
    return preferred_branch
  if viable_tag and tag_exists_in_repo(repo_url, viable_tag):
    return viable_tag

def execute_git_command_for_source(command: str, source: str) -> Tuple[int, str]:
  """
  ### Executes the git command for a specific source.

  #### Params:
  - command (str): Command to execute on the source.
  - source (str): The source repository name.

  #### Returns:
  - (tuple(int, str)): Tuple containing the return code and output message.
  """
  source_path = paths.get_source_path(source)
  if not os.path.exists(source_path):
    logger(logger.yellow(
      f"WARNING: Source {source} does not exist in path {source_path}. Skipping."
    ))
    return 0, ""
  
  return shell_handler.run_shell_command(
    f"git {command}",
    cwd=source_path,
    show_output=True,
    show_error=True
  )

def __ref_exists_in_repo(repo_url: str, ref: str, is_branch: bool) -> bool:
  """
  ### Checks if a given reference exists in the given repository.

  #### Params:
  - repo_url (str): Repository to check from.
  - ref (str): Reference to check for.
  - is_branch (bool): If True, the reference is a branch. If False, it is a tag.

  #### Returns:
  - (bool): True if the ref exists, False otherwise.
  """
  ref_type = "heads" if is_branch else "tags"
  ret_code, output = shell_handler.run_shell_command(
    f"git ls-remote --{ref_type} {repo_url}.git refs/{ref_type}/{ref}"
  )
  if ret_code:
    return False
  return f"refs/{ref_type}/{ref}" in output
