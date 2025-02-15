import os

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants, urls
from xmipp3_installer.installer.modes.mode_sync import mode_sync_executor

from . import mode_sync
from .. import IO_ERROR
from ...test_files import xmipp_sync_data

MODEL_DIR = os.path.join(".", "tests", "e2e", "test_files")
REAL_MODELS_DIR = os.path.join(constants.SOURCES_PATH, constants.XMIPP, "models")
__REAL_SYNC_PROGRAM_PATH = os.path.join(mode_sync_executor._SYNC_PROGRAM_PATH, mode_sync.SYNC_PROGRAM_NAME)
FAKE_SYNC_PROGRAM_FULL_PATH = os.path.join(MODEL_DIR, mode_sync.SYNC_PROGRAM_NAME)

NO_PROGRAM = '\n'.join([
	logger.red(f"{__REAL_SYNC_PROGRAM_PATH} does not exist."),
	logger.red("Xmipp needs to be compiled successfully before running this command!"),
  IO_ERROR,
	""
])

DOWNLOAD = '\n'.join([
	"Downloading Deep Learning models (in background)",
	logger.blue(f"{FAKE_SYNC_PROGRAM_FULL_PATH} download {REAL_MODELS_DIR} {urls.MODELS_URL} DLmodels"),
  xmipp_sync_data.MESSAGE,
	logger.green("Models successfully downloaded!"),
	""
])

UPDATE = '\n'.join([
	"Updating Deep Learning models (in background)",
	logger.blue(f"{FAKE_SYNC_PROGRAM_FULL_PATH} update {REAL_MODELS_DIR} {urls.MODELS_URL} DLmodels"),
  xmipp_sync_data.MESSAGE,
	logger.green("Models successfully updated!"),
	""
])
