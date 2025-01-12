import filecmp
import os
import subprocess

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.repository.config import ConfigurationFileHandler

from .. import (
	get_file_content, normalize_line_endings,
	copy_file_from_reference, delete_paths
)

__DATE = "10-12-2024 17:26.33"

@pytest.mark.parametrize(
	"__setup_config_evironment,expected_file,overwrite",
	[
		pytest.param((False, "default.conf"), "default.conf", False),
		pytest.param((True, "default.conf"), "default.conf", False),
		pytest.param((True, "modified.conf"), "modified.conf", False),
		pytest.param((True, "unknown.conf"), "unknown.conf", False),
		pytest.param((False, "default.conf"), "default.conf", True),
		pytest.param((True, "default.conf"), "default.conf", True),
		pytest.param((True, "modified.conf"), "default.conf", True),
		pytest.param((True, "unknown.conf"), "default.conf", True)
	],
	indirect=["__setup_config_evironment"]
)
def test_writes_expected_config_file(
	__setup_config_evironment,
	expected_file,
	overwrite
):
	command_words = ["xmipp3_installer", "config"]
	if overwrite:
		command_words.append("-o")
	subprocess.run(command_words)
	__change_config_file_date()
	expected_file = __get_test_config_file(expected_file, False)
	normalize_line_endings(expected_file)
	assert (
		filecmp.cmp(
			constants.CONFIG_FILE,
			expected_file,
			shallow=False
		)
	), f"Expected:\n{get_file_content(expected_file)}\n\nReceived:\n{get_file_content(constants.CONFIG_FILE)}"

def __get_test_config_file(file_name, input):
	return os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		"test_files",
		"conf_files",
		"input" if input else "output",
		file_name
	)

def __change_config_file_date():
	file_hanlder = ConfigurationFileHandler()
	old_date = file_hanlder.get_config_date()
	with open(constants.CONFIG_FILE) as config_file:
		content = config_file.read()
	with open(constants.CONFIG_FILE, 'w') as config_file:
		content = content.replace(old_date, __DATE)
		config_file.write(content)

@pytest.fixture(params=[(False, "default.conf")])
def __setup_config_evironment(request):
	exists, copy_name = request.param
	try:
		if not exists:
			delete_paths([constants.CONFIG_FILE])
		else:
			copy_file_from_reference(
				__get_test_config_file(copy_name, True),
				constants.CONFIG_FILE
			)
		yield copy_name
	finally:
		delete_paths([constants.CONFIG_FILE])
