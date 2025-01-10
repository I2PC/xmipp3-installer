import subprocess

from xmipp3_installer.installer.tmp import versions

from .. import get_assertion_message

def test_returns_short_version():
	command_words = ["xmipp3_installer", "version", "--short"]
	result = subprocess.run(command_words, capture_output=True, text=True)
	expected_version = f"{versions.XMIPP_VERSIONS[versions.XMIPP][versions.VERNAME_KEY]}\n"
	assert (
		result.stdout == expected_version
	), get_assertion_message("short version", expected_version, result.stdout)
