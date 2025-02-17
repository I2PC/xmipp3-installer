import filecmp
import os
import subprocess

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.installer import constants
from xmipp3_installer.repository.config import ConfigurationFileHandler
from xmipp3_installer.shared import file_operations

from .. import (
	get_file_content, normalize_file_line_endings,
	get_test_file, copy_file_from_reference
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
	command_words = ["xmipp3_installer", modes.MODE_CONFIG]
	if overwrite:
		command_words.append("-o")
	subprocess.run(command_words, stdout=subprocess.PIPE)
	__change_config_file_date()
	copy_file_from_reference(
		__get_test_config_file(expected_file, False),
		__setup_config_evironment
	)
	normalize_file_line_endings(__setup_config_evironment)
	assert (
		filecmp.cmp(
			constants.CONFIG_FILE,
			__setup_config_evironment,
			shallow=False
		)
	), f"Expected:\n{get_file_content(__setup_config_evironment)}\n\nReceived:\n{get_file_content(constants.CONFIG_FILE)}"

def __get_test_config_file(file_name, input):
	return get_test_file(
		os.path.join(
			"conf_files",
			"input" if input else "output",
			file_name
		)
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
			file_operations.delete_paths([constants.CONFIG_FILE, copy_name])
		else:
			copy_file_from_reference(
				__get_test_config_file(copy_name, True),
				constants.CONFIG_FILE
			)
		yield copy_name
	finally:
		file_operations.delete_paths([constants.CONFIG_FILE, copy_name])
