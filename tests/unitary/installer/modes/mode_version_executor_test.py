import os
from unittest.mock import patch, call

import pytest

from xmipp3_installer.installer.modes.mode_version_executor import ModeVersionExecutor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.tmp import versions
from xmipp3_installer.installer import constants
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.repository import config

from .... import get_assertion_message

__LEFT_TEXT_LEN = 5
__DATE = "dd/mm/yyyy"
__FIXED_DATES_SECTION_PART = f"""Release date: {versions.RELEASE_DATE}
Compilation date: """
__SOURCE = "xmipp-dependency"
__SOURCE_PATH = os.path.join(constants.SOURCES_PATH, __SOURCE)
__COMMIT = "5c3a24f"
__SOURCE_LEFT_TEXT = f"{__SOURCE} branch: "
__TAG_NAME = "tags/v3.24.06-Oceanus"
__BRANCH_NAME = "devel"

def test_implements_interface_mode_executor():
	version_executor = ModeVersionExecutor({})
	assert (
		isinstance(version_executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		version_executor.__class__.__bases__[0].__name__
	)

def test_sets_short_value_false_when_not_provided():
	version_executor = ModeVersionExecutor({})
	assert (
		version_executor.short == False
	), get_assertion_message("short value", False, version_executor.short)

@pytest.mark.parametrize(
	"expected_short",
	[
		pytest.param(False),
		pytest.param(True),
		pytest.param(None)
	]
)
def test_sets_overwrite_value_to_introduced_value_in_args(expected_short):
	version_executor = ModeVersionExecutor({params.PARAM_SHORT: expected_short})
	assert (
		version_executor.short == expected_short
	), get_assertion_message("short value", expected_short, version_executor.short)

@pytest.mark.parametrize(
  "__mock_exists_multiple",
  [
    pytest.param([False, False]),
    pytest.param([False, True]),
    pytest.param([True, False]),
    pytest.param([True, True])
  ],
  indirect=["__mock_exists_multiple"]
)
def test_sets_file_exists_values_as_expected_when_initializing(__mock_exists_multiple):
	version_executor = ModeVersionExecutor({})
	file_exist_values = (version_executor.config_exists, version_executor.version_file_exists)
	expected_values = (
		__mock_exists_multiple(constants.CONFIG_FILE),
		__mock_exists_multiple(constants.LIBRARY_VERSIONS_FILE)
	)
	assert (
		file_exist_values == expected_values
	), get_assertion_message("file exists values", expected_values, file_exist_values)

@pytest.mark.parametrize(
  "__mock_exists_multiple,expected_is_configured",
  [
    pytest.param([False, False], False),
    pytest.param([False, True], False),
    pytest.param([True, False], False),
    pytest.param([True, True], True)
  ],
  indirect=["__mock_exists_multiple"]
)
def test_sets_is_configured_values_as_expected_when_initializing(__mock_exists_multiple, expected_is_configured):
	version_executor = ModeVersionExecutor({})
	assert (
		version_executor.is_configured == expected_is_configured
	), get_assertion_message("is configured values", expected_is_configured, version_executor.is_configured)

def test_does_not_override_parent_config_values(__dummy_test_mode_executor):
	base_executor = __dummy_test_mode_executor({})
	base_executor.run()  # To cover dummy implementation execution
	config_executor = ModeVersionExecutor({})
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit
	)
	inherited_config = (
		config_executor.logs_to_file,
		config_executor.prints_with_substitution,
		config_executor.prints_banner_on_exit
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

@pytest.mark.parametrize(
	"input_text,expected_result",
	[
		pytest.param("", "     "),
		pytest.param("a", "a    "),
		pytest.param("abcde", "abcde"),
		pytest.param("abcdef", "abcdef")
	]
)
def test_returns_expected_text_when_adding_padding_spaces(
	input_text,
	expected_result,
	__mock_left_text_len
):
	version_executor = ModeVersionExecutor({})
	result_text = version_executor._ModeVersionExecutor__add_padding_spaces(input_text)
	assert (
		result_text == expected_result
	), get_assertion_message("padded text", expected_result, result_text)

def test_calls_add_padding_spaces_when_getting_dates_section(
	__mock_add_padding_spaces
):
	version_executor = ModeVersionExecutor({})
	version_executor._ModeVersionExecutor__get_dates_section()
	__mock_add_padding_spaces.assert_has_calls([
		call('Release date: '),
		call('Compilation date: ')
	])

def test_instantiates_configuration_file_handler_when_getting_dates_section_and_config_exists(
	__mock_add_padding_spaces,
	__mock_configuration_file_handler
):
	version_executor = ModeVersionExecutor({})
	version_executor.config_exists = True
	version_executor._ModeVersionExecutor__get_dates_section()
	__mock_configuration_file_handler.assert_called_once_with(path=constants.CONFIG_FILE)

def test_calls_configuration_file_handler_get_config_date_when_getting_dates_section_and_config_exists(
	__mock_add_padding_spaces,
	__mock_configuration_file_handler
):
	version_executor = ModeVersionExecutor({})
	version_executor.config_exists = True
	version_executor._ModeVersionExecutor__get_dates_section()
	__mock_configuration_file_handler().get_config_date.assert_called_once_with()

@pytest.mark.parametrize(
	"config_file_exists,expected_compilation_date",
	[
		pytest.param(False, "-"),
		pytest.param(True, __DATE)
	]
)
def test_returns_expected_dates_section(
	config_file_exists,
	expected_compilation_date,
	__mock_add_padding_spaces,
	__mock_configuration_file_handler
):
	version_executor = ModeVersionExecutor({})
	version_executor.config_exists = config_file_exists
	dates_section = version_executor._ModeVersionExecutor__get_dates_section()
	expected_dates_section = f"{__FIXED_DATES_SECTION_PART}{expected_compilation_date}"
	assert (
		dates_section == expected_dates_section
	), get_assertion_message("dates section", expected_dates_section, dates_section)

def test_calls_add_padding_spaces_when_getting_source_info(
	__mock_add_padding_spaces,
	__mock_exists
):
	__mock_exists.return_value = False
	version_executor = ModeVersionExecutor({})
	version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
	__mock_add_padding_spaces.assert_called_once_with(__SOURCE_LEFT_TEXT)

def test_calls_get_current_commit_when_getting_source_info(
	__mock_add_padding_spaces,
	__mock_exists,
	__mock_get_current_commit,
	__mock_get_commit_branch,
	__mock_get_current_branch,
	__mock_is_tag
):
	version_executor = ModeVersionExecutor({})
	version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
	__mock_get_current_commit.assert_called_once_with(dir=__SOURCE_PATH)

def test_calls_get_commit_branch_when_getting_source_info(
	__mock_add_padding_spaces,
	__mock_exists,
	__mock_get_current_commit,
	__mock_get_commit_branch,
	__mock_get_current_branch,
	__mock_is_tag
):
	version_executor = ModeVersionExecutor({})
	version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
	__mock_get_commit_branch.assert_called_once_with(
		__mock_get_current_commit.return_value,
		dir=__SOURCE_PATH
	)

def test_calls_get_current_branch_when_getting_source_info(
	__mock_add_padding_spaces,
	__mock_exists,
	__mock_get_current_commit,
	__mock_get_commit_branch,
	__mock_get_current_branch,
	__mock_is_tag
):
	version_executor = ModeVersionExecutor({})
	version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
	__mock_get_current_branch.assert_called_once_with(dir=__SOURCE_PATH)

def test_calls_is_tag_when_getting_source_info(
	__mock_add_padding_spaces,
	__mock_exists,
	__mock_get_current_commit,
	__mock_get_commit_branch,
	__mock_get_current_branch,
	__mock_is_tag
):
	version_executor = ModeVersionExecutor({})
	version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
	__mock_is_tag.assert_called_once_with(dir=__SOURCE_PATH)

@pytest.mark.parametrize(
	"__mock_exists,__mock_is_tag,expected_info_right",
	[
		pytest.param(False, False, logger.yellow("Not found")),
		pytest.param(False, True, logger.yellow("Not found")),
		pytest.param(True, False, f"{__BRANCH_NAME} ({__COMMIT})"),
		pytest.param(True, True, f"{__TAG_NAME} ({__COMMIT})"),
	],
	indirect=["__mock_exists", "__mock_is_tag"]
)
def test_returns_expected_source_info(
	expected_info_right,
	__mock_add_padding_spaces,
	__mock_exists,
	__mock_get_current_commit,
	__mock_get_commit_branch,
	__mock_get_current_branch,
	__mock_is_tag
):
	version_executor = ModeVersionExecutor({})
	source_info = version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
	expected_info = f"{__SOURCE_LEFT_TEXT}{expected_info_right}"
	assert (
		source_info == expected_info
	), get_assertion_message("source info", expected_info, source_info)

@pytest.fixture(params=[[True, True]])
def __mock_exists_multiple(request, __mock_exists):
	def __side_effect(path):
		config_file_exists = request.param[0]
		lib_file_exists = request.param[1]
		if path == constants.CONFIG_FILE:
			return config_file_exists
		elif path == constants.LIBRARY_VERSIONS_FILE:
			return lib_file_exists
		else:
			return False
	__mock_exists.side_effect = __side_effect
	yield __mock_exists

@pytest.fixture(params=[True])
def __mock_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return (0, "")
	return TestExecutor

@pytest.fixture
def __mock_left_text_len():
	with patch.object(
		ModeVersionExecutor,
		"_ModeVersionExecutor__LEFT_TEXT_LEN",
		new=__LEFT_TEXT_LEN
	):
		yield

@pytest.fixture
def __mock_add_padding_spaces():
	with patch(
		"xmipp3_installer.installer.modes.mode_version_executor.ModeVersionExecutor._ModeVersionExecutor__add_padding_spaces"
	) as mock_method:
		mock_method.side_effect = lambda text: text
		yield mock_method

@pytest.fixture
def __mock_configuration_file_handler():
	with patch.object(config, "ConfigurationFileHandler") as mock_object:
		instance = mock_object.return_value
		instance.get_config_date.return_value = __DATE
		yield mock_object

@pytest.fixture
def __mock_get_current_commit():
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.get_current_commit"
	) as mock_method:
		mock_method.return_value = __COMMIT
		yield mock_method

@pytest.fixture
def __mock_get_commit_branch(__mock_is_tag):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.get_commit_branch"
	) as mock_method:
		mock_method.return_value = __TAG_NAME if __mock_is_tag.return_value else __BRANCH_NAME
		yield mock_method

@pytest.fixture
def __mock_get_current_branch(__mock_is_tag):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.get_current_branch"
	) as mock_method:
		mock_method.return_value = "HEAD" if __mock_is_tag.return_value else __BRANCH_NAME
		yield mock_method

@pytest.fixture(params=[False])
def __mock_is_tag(request):
	with patch(
		"xmipp3_installer.installer.handlers.git_handler.is_tag"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
