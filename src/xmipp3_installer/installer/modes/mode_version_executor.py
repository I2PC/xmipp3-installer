import os
from typing import Dict, Tuple

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.api_client.assembler import installation_info_assembler
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.installer.handlers import git_handler
from xmipp3_installer.installer.handlers.cmake import cmake_handler
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
			title = f"Xmipp {versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERSION_KEY]} ({version_type})"
			logger(f"{logger.bold(title)}\n")
			logger(self.__get_dates_section())
			system_version_left_text = self.__add_padding_spaces("System version: ")
			logger(f"{system_version_left_text}{installation_info_assembler.get_os_release_name()}")
			logger(f"{self.__get_sources_info()}\n")
			library_file_exists = os.path.exists(constants.LIBRARY_VERSIONS_FILE)
			if library_file_exists:
				logger(self.__get_library_versions_section())
			if not ModeVersionExecutor.__are_all_sources_present() or not library_file_exists:
				logger(self.__get_configuration_warning_message())
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
			return f"{source_left_text}{logger.yellow('Not found')}"
		current_commit = git_handler.get_current_commit(dir=source_path)
		commit_branch = git_handler.get_commit_branch(current_commit, dir=source_path)
		current_branch = git_handler.get_current_branch(dir=source_path)
		display_name = commit_branch if git_handler.is_tag(dir=source_path) else current_branch
		return f"{source_left_text}{display_name} ({current_commit})"

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

	def __get_library_versions_section(self) -> str:
		"""
		### Retrieves the version of the libraries used in the project.
		
		#### Returns:
		- (str): Libraries with their version.
		"""
		if not os.path.exists(constants.LIBRARY_VERSIONS_FILE):
			return ""
		version_lines = [] 
		versions = cmake_handler.get_library_versions_from_cmake_file(constants.LIBRARY_VERSIONS_FILE)
		for library, version in versions.items():
			library_left_text = self.__add_padding_spaces(f"{library}: ")
			version_lines.append(f"{library_left_text}{version}")
		return '\n'.join(version_lines)

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

	def __get_configuration_warning_message(self) -> str:
		"""
		### Returns a message indicating configuration is not complete.

		#### Returns:
		- (str): 
		"""
		return '\n'.join([
			logger.yellow("This project has not yet been configured, so some detectable dependencies have not been properly detected."),
			logger.yellow("Run mode 'getSources' and then 'configBuild' to be able to show all detectable ones.")
		])
