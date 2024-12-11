import filecmp
import os
import shutil
import subprocess

import pytest

from xmipp3_installer.installer import constants
from xmipp3_installer.repository.config import ConfigurationFileHandler

__DATE = "10-12-2024 17:26.33"

@pytest.mark.parametrize(
	"__setup_config_evironment",
	[
		pytest.param((False, "default.conf")),
		pytest.param((True, "default.conf"))
	],
	indirect=["__setup_config_evironment"]
)
def test_writes_expected_config_file(
	__setup_config_evironment
):
	subprocess.run(["xmipp3_installer", "config"])
	__change_config_file_date()
	assert (
		filecmp.cmp(
			constants.CONFIG_FILE,
			__get_test_config_file("default.conf"),
			shallow=False
		)
	)

def __get_test_config_file(file_name):
	return os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		"conf_files",
		file_name
	)

def __delete_config_file(file_name):
	if os.path.exists(file_name):
		os.remove(file_name)

def __copy_file_from_reference(file_name):
	shutil.copyfile(
		__get_test_config_file(file_name),
		constants.CONFIG_FILE
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
			__delete_config_file(constants.CONFIG_FILE)
		else:
			__copy_file_from_reference(copy_name)
		yield
	finally:
		__delete_config_file(constants.CONFIG_FILE)
