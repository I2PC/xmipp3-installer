from .. import (
	JSON_XMIPP_VERSION_NAME, JSON_XMIPP_VERSION_NUMBER,
	JSON_XMIPP_RELEASE_DATE, JSON_XMIPP_CORE_MIN_VERSION
)

class DummyVersionsManager:
	def __init__(self):
		self.xmipp_version_name = JSON_XMIPP_VERSION_NAME
		self.xmipp_version_number = JSON_XMIPP_VERSION_NUMBER
		self.xmipp_release_date = JSON_XMIPP_RELEASE_DATE
		self.xmipp_core_min_version = JSON_XMIPP_CORE_MIN_VERSION
