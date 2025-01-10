import os
from typing import Dict, Tuple

from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.installer.handlers import git_handler
from xmipp3_installer.installer import constants
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.repository import config

class ModeVersionExecutor(mode_executor.ModeExecutor):
	__LEFT_TEXT_LEN = 25

	def __init__(self, args: Dict):
		super().__init__(args)
		self.short = args.get(params.PARAM_SHORT, False)
		self.config_exists = os.path.exists(constants.CONFIG_FILE)
		self.version_file_exists = os.path.exists(constants.LIBRARY_VERSIONS_FILE)
		self.is_configured = self.config_exists and self.version_file_exists
	
	def run(self) -> Tuple[int, str]:
		"""
		### Collects all the version information available and displays it.

		#### Returns:
		- (tuple(int, str)): Tuple containing the error status and an error message if there was an error.
		"""
		if self.short:
			logger(versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERNAME_KEY])
		else:
			version_type = 'release' if git_handler.is_tag() else git_handler.get_current_branch()
			logger(logger.bold(f"Xmipp {versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]} ({version_type})\n"))
			logger(self.__get_dates_section())
			logger(installation_info_assembler.get_os_release_name())
			logger(self.__get_sources_info())
		return 0, ""

	def __get_dates_section(self) -> str:
		"""
		### Returns the message section related to dates.

		#### Returns:
		- (str): Dates related message section.
		"""
		dates_section = f"{self.__add_padding_spaces('Release date: ')}{versions.RELEASE_DATE}\n"
		dates_section += f"{self.__add_padding_spaces('Compilation date: ')}"
		if self.config_exists:
			config_file = config.ConfigurationFileHandler(path=constants.CONFIG_FILE)
			dates_section += config_file.get_config_date()
		else:
			dates_section += "-"
		return dates_section
	
	def __get_sources_info(self) -> str:
		"""
		### Returns the message section related to sources.

		#### Returns:
		- (str): Sources related message section.
		"""
		sources_message_lines = []
		for source_package in constants.XMIPP_SOURCES:
			sources_message_lines.append(self.__get_source_info(source_package))
		return '\n'.join(sources_message_lines)

	def __get_source_info(self, source: str) -> str:
		"""
		### Returns the info message related to a given source.

		#### Params:
		- source (str): Source to get the message about.

		#### Returns:
		- (str): Info message about the given source.
		"""
		source_path = os.path.join(constants.SOURCES_PATH, source)
		source_left_text = self.__add_padding_spaces(f"{source} branch: ")
		if not os.path.exists(source_path):
			return f"{source_left_text}{logger.yellow('Not found')}\n"
		current_commit = git_handler.get_current_commit(dir=source_path)
		commit_branch = git_handler.get_commit_branch(current_commit, dir=source_path)
		current_branch = git_handler.get_current_branch(dir=source_path)
		display_name = commit_branch if git_handler.is_tag(dir=source_path) else current_branch
		return f"{source_left_text}{display_name} ({current_commit})\n"

	@staticmethod
	def __are_all_sources_present() -> bool:
		"""
		### Check if all required source packages are present.

		#### Returns:
		- (bool): True if all source packages are present, False otherwise.
		"""
		for source_package in constants.XMIPP_SOURCES:
			if not os.path.exists(os.path.join(constants.SOURCES_PATH, source_package)):
				return False
		return True

	def __add_padding_spaces(self, left_text: str) -> str:
		"""
		### Adds right padding as spaces to the given text until it reaches the desired length.

		#### Params:
		- left_text (str): Text to add padding to.

		#### Returns:
		- (str): Padded string.
		"""
		text_len = len(left_text)
		if text_len >= self.__LEFT_TEXT_LEN:
			return left_text
		spaces = ''.join([' ' for _ in range(self.__LEFT_TEXT_LEN - text_len)])
		return f"{left_text}{spaces}"
