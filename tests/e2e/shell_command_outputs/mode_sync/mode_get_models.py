import os

from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants, urls

from .. import mode_sync
from ....test_files import xmipp_sync_data
from .... import TEST_FILES_DIR

REAL_MODELS_DIR = os.path.join(constants.SOURCES_PATH, constants.XMIPP, "models")
FAKE_SYNC_PROGRAM_FULL_PATH = os.path.join(TEST_FILES_DIR, mode_sync.SYNC_PROGRAM_NAME)

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
