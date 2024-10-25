"""### Functions that interact with Git via shell."""

from xmipp3_installer.domain.handlers import shell_handler

def get_current_branch(dir: str='./') -> str:
	"""
	### This function returns the current branch of the repository of the given directory or empty string if it is not a repository or a recognizable tag.
	
	#### Params:
	- dir (str): Optional. Directory of the repository to get current branch from. Default is current directory.
	
	#### Returns:
	- (str): The name of the branch, 'HEAD' if a tag, or empty string if given directory is not a repository or a recognizable tag.
	"""
	ret_code, branch_name = shell_handler.run_shell_command("git rev-parse --abbrev-ref HEAD", cwd=dir)
	# If there was an error, we are in no branch
	return branch_name if not ret_code else ''

def is_tag(dir: str='./') -> bool:
	"""
	### This function returns True if the current Xmipp repository is in a tag.

	#### Params:
	- dir (str): Optional. Directory of the repository where the check will happen. Default is current directory.
	
	#### Returns:
	- (bool): True if the repository is a tag. False otherwise.
	"""
	current_branch = get_current_branch(dir=dir)
	return not current_branch or current_branch == "HEAD"

def is_branch_up_to_date(dir: str='./') -> bool:
	"""
	### This function returns True if the current branch is up to date, or False otherwise or if some error happened.
	
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
