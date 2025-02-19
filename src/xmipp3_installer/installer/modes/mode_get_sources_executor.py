from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.handlers import git_handler, versions_manager

class ModeGetSourcesExecutor(mode_executor.ModeExecutor):
	def __init__(self, context: Dict, substitute: bool=False):
		"""
		### Constructor.
		
		#### Params:
		- context (dict): Dictionary containing the installation context variables.
		- substitute (bool): Optional. If True, printed text will be substituted with the next message.
		"""
		super().__init__(context)
		self.substitute = substitute
		self.target_branch = context.pop(params.PARAM_BRANCH)
		versions: versions_manager.VersionsManager = context[constants.VERSIONS_CONTEXT_KEY]
		self.xmipp_tag_name = versions.xmipp_version_name
	
	def run(self) -> Tuple[int, str]:
		"""
		### Executes the given git command into all xmipp source repositories.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		logger(predefined_messages.get_section_message("Getting Xmipp sources"))
		logger(f"Cloning {constants.XMIPP_CORE}...", substitute=self.substitute)
		logger(predefined_messages.get_working_message(), substitute=self.substitute)

		current_branch = git_handler.get_current_branch()
		tag_name = None
		if (
			current_branch and
			current_branch != constants.MASTER_BRANCHNAME and
			current_branch != constants.TAG_BRANCH_NAME
		):
			tag_name = ""
		clone_branch = git_handler.get_clonable_branch("", self.target_branch, tag_name)

		return 0, ""

