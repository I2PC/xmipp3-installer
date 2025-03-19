from xmipp3_installer.installer import constants

from .. import (
  JSON_XMIPP_VERSION_NAME, JSON_XMIPP_VERSION_NUMBER,
  JSON_XMIPP_RELEASE_DATE, JSON_XMIPP_CORE_TARGET_TAG, JSON_XMIPP_VIZ_TARGET_TAG
)

class DummyVersionsManager:
  def __init__(self):
    self.xmipp_version_name = JSON_XMIPP_VERSION_NAME
    self.xmipp_version_number = JSON_XMIPP_VERSION_NUMBER
    self.xmipp_release_date = JSON_XMIPP_RELEASE_DATE
    self.sources_versions = {
      constants.XMIPP_CORE: JSON_XMIPP_CORE_TARGET_TAG,
      constants.XMIPP_VIZ: JSON_XMIPP_VIZ_TARGET_TAG
    }
