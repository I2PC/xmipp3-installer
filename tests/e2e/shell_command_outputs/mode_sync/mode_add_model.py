from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer.constants import paths

from ... import shell_command_outputs

LOGIN = "test@test.com"
MODEL_NAME = "fake-model"
NON_EXISTING_MODEL_PATH = "./does-not-exist"

__CANCELLED_ERROR = logger.red("Error -1: Process was interrupted by the user.")

__NO_MODEL_INITIAL_MESSAGE = f"{NON_EXISTING_MODEL_PATH} is not a directory. Please, check the path."
NO_MODEL = f"""{logger.red(__NO_MODEL_INITIAL_MESSAGE)}
{logger.red("The name of the model will be the name of that folder.")}
{shell_command_outputs.IO_ERROR}
"""

__PRE_CONFIRMATION_WARNING = f"""Creating the xmipp_model_{MODEL_NAME}.tgz model.
{logger.yellow("Warning: Uploading, please BE CAREFUL! This can be dangerous.")}
You are going to be connected to {LOGIN} to write in folder {paths.SCIPION_SOFTWARE_EM}.
Continue? YES/no (case sensitive)
"""

CANCELLED = f"{__PRE_CONFIRMATION_WARNING}{__CANCELLED_ERROR}\n"

__SUCCESS_MESSAGE = logger.green(f"{MODEL_NAME} model successfully uploaded! Removing the local .tgz")
UPLOADED = f"""{__PRE_CONFIRMATION_WARNING}Trying to upload the model using test@test.com as login
{__SUCCESS_MESSAGE}
"""
