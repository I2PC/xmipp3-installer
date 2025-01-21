import os
import tarfile
from typing import Dict, Tuple

from xmipp3_installer.application.logger import errors
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.handlers import shell_handler

class ModeAddModelExecutor(mode_executor.ModeExecutor):
	__SYNC_PROGRAM_PATH = os.path.join(".", "dist", "bin", "xmipp_sync_data")

	def __init__(self, args: Dict):
		"""
		### Constructor.
		
		#### Params:
		- args (dict): Dictionary containing all parsed command-line arguments.
		"""
		super().__init__(args)
		self.login = args.pop(params.PARAM_LOGIN)
		self.model_path = args.pop(params.PARAM_MODEL_PATH)
		self.update = args.pop(params.PARAM_UPDATE, False)
		self.model_dir = os.path.dirname(self.model_path)
		self.model_name = os.path.basename(self.model_path)
		self.tar_file_name = f"xmipp_model_{self.model_name}.tgz"
		self.tar_file_path = os.path.join(self.model_dir, self.tar_file_name)
	
	def run(self) -> Tuple[int, str]:
		"""
		### Uploads the model to the remote server.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		if not os.path.isdir(self.model_path):
			logger('\n'.join([
				logger.red(f"{self.model_path} is not a directory. Please, check the path."),
				logger.red("The name of the model will be the name of that folder.")
			]))
			return errors.IO_ERROR, ""
		
		if not os.path.exists(self.__SYNC_PROGRAM_PATH):
			logger('\n'.join([
				logger.red(f"{self.__SYNC_PROGRAM_PATH} does not exist."),
				logger.red("Xmipp needs to be compiled successfully before running this command!")
			]))
			return errors.IO_ERROR, ""
		
		ret_code, output = self.__generate_compressed_file()
		if ret_code:
			return ret_code, output
		
		if not self.__get_confirmation():
			return errors.INTERRUPTED_ERROR, ""
		
		return self.__upload_model()
	
	def __generate_compressed_file(self) -> Tuple[int, str]:
		"""
		### Generates the model's compressed file.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		logger(f"Creating the {self.tar_file_name} model.")
		try:
			with tarfile.open(self.tar_file_path, "w:gz") as tar:
				tar.add(self.model_path, arcname=self.model_name)
		except (tarfile.ReadError, tarfile.CompressionError) as ex:
			return errors.IO_ERROR, str(ex)
		return 0, ""
	
	def __get_confirmation(self) -> bool:
		"""
		### Asks the user for confirmation.

		#### Returns:
		- (bool): True if the user confirms, False otherwise.
		"""
		logger('\n'.join([
			logger.yellow("Warning: Uploading, please BE CAREFUL! This can be dangerous."),
			f"You are going to be connected to {self.login} to write in folder {constants.SCIPION_SOFTWARE_EM}.",
			"Continue? YES/no (case sensitive)"
		]))
		return input() == 'YES'

	def __upload_model(self) -> Tuple[int, str]:
		"""
		### Uploads the model to the remote server.

		#### Returns:
		- (tuple(int, str)): Tuple containing the return code and an error message if there was an error.
		"""
		update = '--update' if self.update else ''
		args = f"{self.login}, {os.path.abspath(self.tar_file_path)}, {constants.SCIPION_SOFTWARE_EM}, {update}"	
		logger(f"Trying to upload the model using {self.login} as login")
		ret_code, output = shell_handler.run_shell_command(f"{self.__SYNC_PROGRAM_PATH} upload {args}")
		if not ret_code:
			output = ""
			logger(logger.green(f"{self.model_name} model successfully uploaded! Removing the local .tgz"))
			os.remove(self.tar_file_path)
		return ret_code, output
