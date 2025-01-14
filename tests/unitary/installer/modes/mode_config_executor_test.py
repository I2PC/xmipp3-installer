from unittest.mock import patch, MagicMock, call

import pytest

from xmipp3_installer.installer.modes.mode_config_executor import ModeConfigExecutor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger import errors
from xmipp3_installer.repository import config

from .... import get_assertion_message

__PERMISSION_ERROR_MESSAGE = "Cannot open that file."
__CONFIG_VALUES = {"key1": "value1", "key2": "value2"}
__FILE_FROM_SCRATCH_MESSAGE = "Generating config file from scratch with default values..."
__READ_FILE_MESSAGE = "Reading config file..."

def test_implements_interface_mode_executor():
	config_executor = ModeConfigExecutor({})
	assert (
		isinstance(config_executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		config_executor.__class__.__bases__[0].__name__
	)

def test_sets_overwrite_value_false_when_not_provided():
	config_executor = ModeConfigExecutor({})
	assert (
		config_executor.overwrite == False
	), get_assertion_message("overwrite value", False, config_executor.overwrite)

@pytest.mark.parametrize(
	"expected_overwrite",
	[
		pytest.param(False),
		pytest.param(True),
		pytest.param(None)
	]
)
def test_sets_overwrite_value_to_introduced_value_in_args(expected_overwrite):
	config_executor = ModeConfigExecutor({params.PARAM_OVERWRITE: expected_overwrite})
	assert (
		config_executor.overwrite == expected_overwrite
	), get_assertion_message("overwrite value", expected_overwrite, config_executor.overwrite)

def test_sets_config_values_empty_when_initializing():
	config_executor = ModeConfigExecutor({})
	assert (
		config_executor.config_values == {}
	), get_assertion_message("config values", {}, config_executor.config_values)

def test_does_not_override_parent_config_values(__dummy_test_mode_executor):
	base_executor = __dummy_test_mode_executor({})
	base_executor.run()  # To cover dummy implementation execution
	config_executor = ModeConfigExecutor({})
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

def test_calls_get_section_message_when_running_executor(
	__mock_logger,
	__mock_configuration_file_handler,
	__mock_get_section_message
):
	config_executor = ModeConfigExecutor({})
	config_executor.run()
	__mock_get_section_message.assert_called_once_with("Managing config file")

def test_calls_get_done_message_when_running_executor(
	__mock_logger,
	__mock_configuration_file_handler,
	__mock_get_done_message
):
	config_executor = ModeConfigExecutor({})
	config_executor.run()
	__mock_get_done_message.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_exists,mode_overwrite,expected_message",
	[
		pytest.param(False, False, __FILE_FROM_SCRATCH_MESSAGE),
		pytest.param(False, True, __FILE_FROM_SCRATCH_MESSAGE),
		pytest.param(True, False, __READ_FILE_MESSAGE),
		pytest.param(True, True, __FILE_FROM_SCRATCH_MESSAGE)
	],
	indirect=["__mock_exists"]
)
def test_calls_logger_when_running_executor(
	__mock_exists,
	mode_overwrite,
	expected_message,
	__mock_logger,
	__mock_configuration_file_handler,
	__mock_get_section_message,
	__mock_get_done_message
):
	config_executor = ModeConfigExecutor({'overwrite': mode_overwrite})
	config_executor.run()
	expected_calls = [
		call(__mock_get_section_message("Managing config file")),
		call(expected_message),
		call(__mock_get_done_message())
	]
	__mock_logger.assert_has_calls(expected_calls)
	assert (
		__mock_logger.call_count == len(expected_calls)
	), get_assertion_message("call count", expected_calls, __mock_logger.call_count)

def test_calls_configuration_file_handler_when_running_executor(
	__mock_configuration_file_handler,
	__mock_logger
):
	config_executor = ModeConfigExecutor({})
	config_executor.run()
	__mock_configuration_file_handler.assert_called_once_with()

def test_calls_configuration_file_handler_write_config_when_running_executor(
	__mock_configuration_file_handler,
	__mock_logger
):
	config_executor = ModeConfigExecutor({})
	config_executor.run()
	__mock_configuration_file_handler().write_config.assert_called_once_with(
		overwrite=config_executor.overwrite
	)

@pytest.mark.parametrize(
	"__mock_configuration_file_handler,expected_config_values",
	[
		pytest.param(False, __CONFIG_VALUES),
		pytest.param(True, {})
	],
	indirect=["__mock_configuration_file_handler"]
)
def test_stores_expected_config_values_when_running_executor(
	__mock_configuration_file_handler,
	expected_config_values,
	__mock_logger
):
	config_executor = ModeConfigExecutor({})
	config_executor.run()
	assert (
		config_executor.config_values == expected_config_values
	), get_assertion_message(
		"stored config values",
		expected_config_values,
		config_executor.config_values
	)

@pytest.mark.parametrize(
	"__mock_configuration_file_handler,expected_values",
	[
		pytest.param(False, (0, "")),
		pytest.param(True, (errors.IO_ERROR, __PERMISSION_ERROR_MESSAGE))
	],
	indirect=["__mock_configuration_file_handler"]
)
def test_returns_expected_values_when_running_executor(
	__mock_configuration_file_handler,
	expected_values,
	__mock_logger
):
	config_executor = ModeConfigExecutor({})
	values = config_executor.run()
	assert (
		values == expected_values
	), get_assertion_message("run values", expected_values, values)

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return (0, "")
	return TestExecutor

@pytest.fixture(params=[False])
def __mock_configuration_file_handler(request):
	mock_handler = MagicMock()
	mock_handler.values = __CONFIG_VALUES
	with patch.object(config, "ConfigurationFileHandler") as mock_object:
		if request.param:
			mock_object.side_effect = PermissionError(__PERMISSION_ERROR_MESSAGE)
		else:
			mock_object.return_value = mock_handler
		yield mock_object

@pytest.fixture
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_get_section_message():
	with patch(
		"xmipp3_installer.application.logger.predefined_messages.get_section_message"
	) as mock_method:
		mock_method.side_effect = lambda text: f"section-{text}-section"
		yield mock_method

@pytest.fixture
def __mock_get_done_message():
	with patch(
		"xmipp3_installer.application.logger.predefined_messages.get_done_message"
	) as mock_method:
		mock_method.return_value = "done message"
		yield mock_method

@pytest.fixture(params=[True])
def __mock_exists(request):
	with patch("os.path.exists") as mock_method:
		mock_method.return_value = request.param
		yield mock_method
