from unittest.mock import patch, MagicMock

import pytest

from xmipp3_installer.application.cli.arguments import modes
from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import installer_service, constants
from xmipp3_installer.installer.modes import mode_selector
from xmipp3_installer.repository.config_vars import variables

from ... import get_assertion_message

__MODE_NAME = "mode1"
__SELECTED_MODE_MESASGE = "selected mode"
__MODE_ALL_MESSAGE = "mode all"
__INSTALLATION_INFO = {
	'user': 'some-user-id'
}
__SEND_INSTALLATION_INFO_KEY = "send-info"
__CONFIG_VALUES = {
	'key1': 'value1',
	'key2': 'value2'
}
__ARGS = {
	"mode": modes.MODE_ALL,
	"variable1": "value1"
}

@pytest.mark.parametrize(
	"expected_mode",
	[pytest.param('all'), pytest.param(__MODE_NAME)]
)
def test_stores_expected_mode_when_initializing(expected_mode, __mock_mode_executors):
	installation_manager = installer_service.InstallationManager({'mode': expected_mode})
	assert (
		installation_manager.mode == expected_mode
	), get_assertion_message("stored mode", expected_mode, installation_manager.mode)

@pytest.mark.parametrize(
	"mode",
	[pytest.param('all'), pytest.param(__MODE_NAME)]
)
def test_stores_expected_mode_executor_when_initializing(mode, __mock_mode_executors):
	args = {'mode': mode}
	installation_manager = installer_service.InstallationManager(args)
	expected_mode = __mock_mode_executors[mode](args)
	assert (
		installation_manager.mode_executor == expected_mode
	), get_assertion_message("stored mode executor", expected_mode, installation_manager.mode_executor)

def test_initializes_config_file_handler_when_initializing(
	__mock_mode_executors,
	__mock_configuration_file_handler
):
	installer_service.InstallationManager({})
	__mock_configuration_file_handler.assert_called_once_with(path=constants.CONFIG_FILE, show_errors=False)

def test_stores_installation_context_when_initializing(
	__mock_mode_executors,
	__mock_configuration_file_handler
):
	installation_manager = installer_service.InstallationManager(__ARGS.copy())
	expected_args = __ARGS.copy()
	expected_args.pop("mode")
	expected_context = {**expected_args, **__mock_configuration_file_handler().values}
	assert (
		installation_manager.context == expected_context
	), get_assertion_message(
		"stored config values",
		expected_context,
		installation_manager.context
	)

@pytest.mark.parametrize(
	"args,expected_executor_key",
	[
		pytest.param({}, modes.MODE_ALL),
		pytest.param({modes.MODE: modes.MODE_ALL}, modes.MODE_ALL),
		pytest.param({modes.MODE: __MODE_NAME}, __MODE_NAME)
	]
)
def test_calls_expected_executor_run_when_running_installer(
	args,
	expected_executor_key,
	__mock_mode_executors
):
	installation_manager = installer_service.InstallationManager(args)
	installation_manager.run_installer()
	expected_executor = __mock_mode_executors[expected_executor_key](args)
	expected_executor.run.assert_called_once_with()

@pytest.mark.parametrize(
	"args,other_executor_key",
	[
		pytest.param({}, __MODE_NAME),
		pytest.param({modes.MODE: modes.MODE_ALL}, __MODE_NAME),
		pytest.param({modes.MODE: __MODE_NAME}, modes.MODE_ALL)
	]
)
def test_does_not_call_other_executor_run_when_running_installer(
	args,
	other_executor_key,
	__mock_mode_executors
):
	installation_manager = installer_service.InstallationManager(args)
	installation_manager.run_installer()
	expected_executor = __mock_mode_executors[other_executor_key](args)
	expected_executor.run.assert_not_called()

@pytest.mark.parametrize(
	"__mock_mode_executors,expected_add_portal_link",
	[
		pytest.param((0, 1), True),
		pytest.param((0, errors.INTERRUPTED_ERROR), False),
	],
	indirect=["__mock_mode_executors"]
)
def test_calls_logger_log_error_when_running_installer_with_non_zero_ret_code(
	__mock_mode_executors,
	expected_add_portal_link,
	__mock_logger_log_error
):
	installation_manager = installer_service.InstallationManager({})
	installation_manager.run_installer()
	executor = __mock_mode_executors[modes.MODE_ALL]({})
	ret_code, output = executor.run()
	__mock_logger_log_error.assert_called_once_with(
		output,
		ret_code=ret_code,
		add_portal_link=expected_add_portal_link
	)

@pytest.mark.parametrize("prints_message", [pytest.param(False), pytest.param(True)])
def test_calls_get_success_message_when_running_executor_with_zero_exit_code_deppending_on_attribute(
	prints_message,
	__mock_mode_executors,
	__mock_get_success_message,
	__mock_logger
):
	__mock_mode_executors['all'](None).prints_banner_on_exit = prints_message
	installation_manager = installer_service.InstallationManager({})
	installation_manager.run_installer()
	if prints_message:
		__mock_get_success_message.assert_called_once_with()
	else:
		__mock_get_success_message.assert_not_called()

@pytest.mark.parametrize(
	"ret_code,sends_installation_info,config_sends_installation_info",
	[
		pytest.param(0, False, False),
		pytest.param(0, False, True),
		pytest.param(0, True, False),
		pytest.param(0, True, True),
		pytest.param(1, False, False),
		pytest.param(1, False, True),
		pytest.param(1, True, False),
		pytest.param(1, True, True)
	]
)
def test_calls_get_installation_info_when_running_executor_deppending_on_attributes(
	__mock_mode_executors,
	ret_code,
	sends_installation_info,
	config_sends_installation_info,
	__mock_logger_log_error,
	__mock_logger,
	__mock_get_installation_info
):
	all_executor = __mock_mode_executors['all'](None)
	all_executor.sends_installation_info = sends_installation_info
	all_executor.run.return_value = (ret_code, "")
	installation_manager = installer_service.InstallationManager({})
	installation_manager.context = {__SEND_INSTALLATION_INFO_KEY: config_sends_installation_info}
	installation_manager.run_installer()
	if sends_installation_info and config_sends_installation_info:
		__mock_get_installation_info.assert_called_once_with(ret_code=ret_code)
	else:
		__mock_get_installation_info.assert_not_called()

@pytest.mark.parametrize(
	"sends_info,config_sends_info",
	[
		pytest.param(False, False),
		pytest.param(False, True),
		pytest.param(True, False),
		pytest.param(True, True)
	]
)
def test_calls_send_installation_attempt_when_running_executor_deppending_on_attribute(
	sends_info,
	config_sends_info,
	__mock_mode_executors,
	__mock_logger,
	__mock_get_installation_info,
	__mock_send_installation_info
):
	__mock_mode_executors['all'](None).sends_installation_info = sends_info
	installation_manager = installer_service.InstallationManager({})
	installation_manager.context = {__SEND_INSTALLATION_INFO_KEY: config_sends_info}
	installation_manager.run_installer()
	if sends_info and config_sends_info:
		__mock_send_installation_info.assert_called_once_with(__mock_get_installation_info())
	else:
		__mock_send_installation_info.assert_not_called()

@pytest.mark.parametrize(
	"sends_info,config_sends_info",
	[
		pytest.param(False, False),
		pytest.param(False, True),
		pytest.param(True, False),
		pytest.param(True, True)
	]
)
def test_calls_logger_when_running_executor_deppending_on_attribute(
	sends_info,
	config_sends_info,
	__mock_mode_executors,
	__mock_logger_log_error,
	__mock_logger,
	__mock_get_installation_info,
	__mock_send_installation_info
):
	__mock_mode_executors['all'](None).sends_installation_info = sends_info
	installation_manager = installer_service.InstallationManager({})
	installation_manager.context = {__SEND_INSTALLATION_INFO_KEY: config_sends_info}
	installation_manager.run_installer()
	if sends_info and config_sends_info:
		__mock_logger.assert_called_once_with("Sending anonymous installation info...")
	else:
		__mock_logger.assert_not_called()

@pytest.mark.parametrize(
	"__mock_mode_executors",
	[
		pytest.param((0, 0)),
		pytest.param((0, 1))
	],
	indirect=["__mock_mode_executors"]
)
def test_returns_run_return_code(
	__mock_mode_executors,
	__mock_logger_log_error,
	__mock_get_success_message,
	__mock_logger
):
	executor = __mock_mode_executors[modes.MODE_ALL]({})
	expected_ret_code, _ = executor.run()
	installation_manager = installer_service.InstallationManager({})
	ret_code = installation_manager.run_installer()
	assert (
		ret_code == expected_ret_code
	), get_assertion_message("return code", expected_ret_code, ret_code)

def test_calls_logger_error_when_running_installer_and_user_interrupts_execution(
	__mock_mode_executors_interrupted,
	__mock_logger_log_error
):
	installation_manager = installer_service.InstallationManager({})
	installation_manager.run_installer()
	__mock_logger_log_error.assert_called_once_with(
		"", ret_code=errors.INTERRUPTED_ERROR, add_portal_link=False
	)

def test_returns_interrupted_error_when_running_installer_and_user_interrupts_execution(
	__mock_mode_executors_interrupted,
	__mock_logger_log_error
):
	installation_manager = installer_service.InstallationManager({})
	ret_code = installation_manager.run_installer()
	assert (
		ret_code == errors.INTERRUPTED_ERROR
	), get_assertion_message("return code", errors.INTERRUPTED_ERROR, ret_code)

def __mock_executor(ret_code, message):
	executor = MagicMock()
	executor.run.return_value = (ret_code, message)
	executor.prints_banner_on_exit = False
	executor.sends_installation_info = False
	return executor

@pytest.fixture(params=[(0, 0)])
def __mock_mode_executors(request):
	selected_executor = __mock_executor(request.param[0], __SELECTED_MODE_MESASGE)
	all_executor = __mock_executor(request.param[1], __MODE_ALL_MESSAGE)
	with patch.object(mode_selector, 'MODE_EXECUTORS', {
		__MODE_NAME: lambda _: selected_executor,
		modes.MODE_ALL: lambda _: all_executor
	}) as mock_object:
		yield mock_object

@pytest.fixture
def __mock_logger_log_error():
	with patch(
		'xmipp3_installer.application.logger.logger.Logger.log_error'
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_get_success_message():
	with patch(
		"xmipp3_installer.application.logger.predefined_messages.get_success_message"
	) as mock_method:
		mock_method.return_value = "success message"
		yield mock_method

@pytest.fixture
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_send_installation_info():
	with patch(
		"xmipp3_installer.api_client.api_client.send_installation_attempt"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_installation_info():
	with patch(
		"xmipp3_installer.api_client.assembler.installation_info_assembler.get_installation_info"
	) as mock_method:
		mock_method.return_value = __INSTALLATION_INFO
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_configuration_file_handler():
	with patch(
		"xmipp3_installer.repository.config.ConfigurationFileHandler"
	) as mock_class:
		mock_class.return_value.values = __CONFIG_VALUES
		yield mock_class

@pytest.fixture(autouse=True)
def __mock_variable_send_installation_info():
	with patch.object(
		variables,
		"SEND_INSTALLATION_STATISTICS",
		__SEND_INSTALLATION_INFO_KEY
	):
		yield __SEND_INSTALLATION_INFO_KEY

@pytest.fixture
def __mock_mode_executors_interrupted(
	__mock_mode_executors
):
	__mock_mode_executors[modes.MODE_ALL]({}).run.side_effect = KeyboardInterrupt
	__mock_mode_executors[__MODE_NAME]({}).run.side_effect = KeyboardInterrupt
	yield __mock_mode_executors
