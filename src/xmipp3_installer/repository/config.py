"""# Contains the configuration file singleton that interact with the configuration file."""

import re
import os
from typing import List, Optional, Tuple, Dict, Any

from xmipp3_installer.shared.singleton import Singleton
from xmipp3_installer.installer import constants
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.repository.config_vars import default_values, variables
from xmipp3_installer.repository.invalid_config_line import InvalidConfigLineError

class ConfigurationFile(Singleton):
	"""
	### Configuration file class for loading and storing the installation configuration.
	"""
	__COMMENT_ESCAPE = '#'
	__ASSIGNMENT_SEPARATOR = '='
	__LAST_MODIFIED_TEXT = "Config file automatically generated on"

	def __init__(self, path: str=constants.CONFIG_FILE):
		"""
		### Constructor.
		
		#### Params:
		- path (str): Optional. Path to the configuration file.
		"""
		self.__path = path
		self.config_variables = {}
		self.read_config()
		self.config_date = self.__read_config_date()

	def read_config(self):
		"""
		### Reads the config file and stores a dictionary with all the parsed variables.
		"""
		file_lines = self.__get_file_content()
		result = {}
		for line_number, line in enumerate(file_lines):
			try:
				key_value_pair = self.__parse_config_line(line, line_number + 1)
			except InvalidConfigLineError as error:
				logger(str(error))
				result = {}
				break
			if key_value_pair:
				key, value = key_value_pair
				result[key] = value
		self.config_variables = {**default_values.CONFIG_DEFAULT_VALUES, **result}

	def writeConfig(self):
		"""
		### Writes a template config file with stored variables, leaving the rest with default values.
		"""
		config_variables = self.config_variables.copy()
		lines = ["##### TOGGLE SECTION #####\n"]
		lines.append(f"# Activate or deactivate this features using values {default_values.ON}/{default_values.OFF}\n")
		lines.extend(self.__get_toggle_lines(variables.TOGGLES, config_variables))

		lines.append("\n##### PACKAGE HOME SECTION #####\n")
		lines.append("# Use this variables to use custom installation paths for the required packages.\n")
		lines.append("# If left empty, CMake will search for those packages within your system.\n")
		lines.extend(self.__get_toggle_lines(variables.LOCATIONS, config_variables))
		
		lines.append("\n##### COMPILATION FLAGS #####\n")
		lines.append("# We recommend not modifying this variables unless you know what you are doing.\n")
		lines.extend(self.__get_toggle_lines(variables.COMPILATION_FLAGS, config_variables))
		
		if config_variables:
			lines.append("\n##### UNKNOWN VARIABLES #####\n")
			lines.append("# This variables were not expected, but are kept here in case they might be needed.\n")
			lines.extend(self.__get_unkown_variable_lines(config_variables))

		lines.append(f"\n# {self.__LAST_MODIFIED_TEXT} {datetime.today()}\n")
		with open(self.__path, 'w') as configFile:
			configFile.writelines(lines)

	def get_config_date(self) -> str:
		"""
		### Returns the date of the last modification of the configuration file.

		#### Returns:
		- (str): Date in dd-mm-yyyy format.
		"""
		if not self.config_date:
			self.config_date = self.__read_config_date()
		return self.config_date
		
	def __get_file_content(self) -> List[str]:
		"""
		### Reads the whole unparsed content of the given file.

		#### Returns:
		- (list(str)): Content of the file, where each line is a string in the result list.
		"""
		if not os.path.exists(self.__path):
			return []
		lines = []
		with open(self.__path, "r") as config_file:
			lines = config_file.readlines()
		return lines

	def __read_config_date(self) -> str:
		"""
		### Reads from the config file the date of its last modification.

		#### Returns:
		- (str): Date in dd-mm-yyyy format.
		"""
		config_lines = self.__get_file_content()
		for line in config_lines:
			if self.__LAST_MODIFIED_TEXT not in line:
				continue
			match = re.search(r'\d{2}-\d{2}-\d{4}', line)
			if match:
				return match.group()
		return ""

	def __parse_config_line(self, line: str, line_number: int) -> Optional[Tuple[str, str]]:
		"""
		### Reads the given line from the config file and returns the key-value pair as a tuple.

		#### Params:
		- line_number (int): Line number inside the config file.
		- line (str): Line to parse.
		
		#### Returns:
		- (tuple(str, str) | None): Tuple containing the read key-value pair if line contains valid data.

		#### Raises:
		- RuntimeError: Raised when a line has an invalid format and cannot be parsed.
		"""
		line_without_comments = line.split(self.__COMMENT_ESCAPE, maxsplit=2)[0].strip()
		if not line_without_comments:
			return None
		
		tokens = line_without_comments.split(self.__ASSIGNMENT_SEPARATOR, maxsplit=1)
		if len(tokens) != 2:
			raise InvalidConfigLineError(
				InvalidConfigLineError.generate_error_message(
					constants.CONFIG_FILE,
					line_number,
					line
				)
			)
		
		return tokens[0].strip(), tokens[1].strip()

	def __make_config_line(self, key: str, value: str, default_value: str) -> str:
		"""
		### Composes a config file line given a key-value pair to write.

		#### Params:
		- key (int): Name of the variable.
		- value (str): Value of the variable found in the config file.
		- default_value (str): Default value of the variable.
		
		#### Returns:
		- (str): String containing the appropiately formatted key-value pair.
		"""
		default_value = '' if default_value is None else default_value
		value = default_value if value is None else value
		return f"{key}{self.__ASSIGNMENT_SEPARATOR}{value}" if key else ""

	def __get_toggle_lines(self, section_type: str, config_variables: Dict[str, Any]) -> List[str]:
		"""
		### Returns the lines composed by the given section's variables in the dictionary, and deletes them from it.

		#### Params:
		- section_type (str): Section to extract variables from.
		- config_variables (dict(str, any)): Dictionary containing all variables.

		#### Returns:
		- (list(str)): Config file lines created from the dictionary variables.
		"""
		lines = []
		for section_variable in variables.CONFIG_VARIABLES[section_type]:
			lines.append(f"{self.__make_config_line(
				section_variable,
				config_variables.get(section_variable),
				default_values.CONFIG_DEFAULT_VALUES[section_variable]
			)}\n")
			config_variables.pop(section_variable, None)
		return lines

	def __get_unkown_variable_lines(self, config_variables: Dict[str, Any]) -> List[str]:
		"""
		### Returns the lines composed by the unkown variables in the dictionary.

		#### Params:
		- config_variables (dict(str, any)): Dictionary containing all unknown variables.

		#### Returns:
		- (list(str)): Config file lines created from the dictionary variables.
		"""
		lines = []
		for variable in config_variables.keys():
			lines.append(
				f"{self.__make_config_line(variable, config_variables[variable], '')}\n"
			)
		return lines