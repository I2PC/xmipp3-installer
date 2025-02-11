import os
from unittest.mock import patch

import pytest

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes import mode_executor
from xmipp3_installer.installer.modes.mode_models import mode_models_executor
from xmipp3_installer.installer.modes.mode_models.mode_models_executor import ModeModelsExecutor

from ..... import get_assertion_message

__SYNC_PROGRAM_PATH = os.path.join(
	mode_models_executor._SYNC_PROGRAM_PATH,
	mode_models_executor._SYNC_PROGRAM_NAME
)

class DummyModelsExecutor(ModeModelsExecutor):
	def _execute_model_operation(self):
		return 0, ""

def test_is_instance_of_mode_executor():
	executor = DummyModelsExecutor({})
	executor._execute_model_operation() # To cover dummy implementation
	assert (
		isinstance(executor, mode_executor.ModeExecutor)
	), get_assertion_message(
		"parent class",
		mode_executor.ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_raises_exception_when_execute_model_operation_not_implemented():
	with pytest.raises(TypeError):
		ModeModelsExecutor({})

def test_does_not_override_parent_config_values(
	__dummy_test_mode_executor
):
	base_executor = __dummy_test_mode_executor({})
	base_executor.run() # To cover dummy implementation execution
	models_executor = DummyModelsExecutor({})
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit
	)
	inherited_config = (
		models_executor.logs_to_file,
		models_executor.prints_with_substitution,
		models_executor.prints_banner_on_exit
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_sets_sync_program_path_when_initializing():
	executor = DummyModelsExecutor({})
	assert (
		executor.sync_program_path == __SYNC_PROGRAM_PATH
	), get_assertion_message(
		"sync program path",
		__SYNC_PROGRAM_PATH,
		executor.sync_program_path
	)

def test_calls_logger_when_sync_program_not_exists(
	__mock_os_path_exists,
	__mock_logger,
	__mock_logger_red
):
	__mock_os_path_exists.return_value = False
	DummyModelsExecutor({}).run()
	error_message = __mock_logger_red(f"{__SYNC_PROGRAM_PATH} does not exist.")
	error_message += "\n"
	error_message += __mock_logger_red("Xmipp needs to be compiled successfully before running this command!")
	__mock_logger.assert_called_once_with(error_message)

def test_returns_error_when_sync_program_not_exists(
	__mock_os_path_exists
):
	__mock_os_path_exists.return_value = False
	executor = DummyModelsExecutor({})
	ret_code, output = executor.run()
	assert (
		(ret_code, output) == (errors.IO_ERROR, "")
	), get_assertion_message("return values", (errors.IO_ERROR, ""), (ret_code, output))

def test_calls_execute_model_operation_when_sync_program_exists(
	__mock_os_path_exists,
	__mock_execute_model_operation
):
	__mock_os_path_exists.return_value = True
	DummyModelsExecutor({}).run()
	__mock_execute_model_operation.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_execute_model_operation",
	[
		pytest.param((0, "success")), pytest.param((1, "failure"))
	],
	indirect=["__mock_execute_model_operation"]
)
def test_returns_execute_model_operation_result_when_sync_program_exists(
	__mock_os_path_exists,
	__mock_execute_model_operation
):
	__mock_os_path_exists.return_value = True
	ret_code, output = DummyModelsExecutor({}).run()
	assert (
		(ret_code, output) == __mock_execute_model_operation()
	), get_assertion_message(
		"model operation output",
		__mock_execute_model_operation(),
		(ret_code, output)
	)

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(mode_executor.ModeExecutor):
		def run(self):
			return (0, "")
	return TestExecutor

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_red():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.red"
	) as mock_method:
		mock_method.side_effect = lambda text: f"red-{text}-red"
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_exists():
	with patch("os.path.exists") as mock_method:
		yield mock_method

@pytest.fixture(params=[(0, "")])
def __mock_execute_model_operation(request):
	with patch(
		"tests.unitary.installer.modes.mode_models.mode_models_executor_test.DummyModelsExecutor._execute_model_operation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method
