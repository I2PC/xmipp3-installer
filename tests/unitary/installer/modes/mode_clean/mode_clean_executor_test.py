from unittest.mock import patch

import pytest

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_clean.mode_clean_executor import ModeCleanExecutor

from ..... import get_assertion_message

def test_is_instance_of_mode_executor(__dummy_test_mode_clean_executor):
	executor = __dummy_test_mode_clean_executor({})
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_raises_exception_when_run_method_not_implemented(
	__no_implementation_child
):
	with pytest.raises(TypeError):
		__no_implementation_child({})

def test_does_not_override_parent_config_values(
	__dummy_test_mode_clean_executor,
	__dummy_test_mode_executor
):
	base_executor = __dummy_test_mode_executor({})
	clean_executor = __dummy_test_mode_clean_executor({})
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit,
		base_executor.sends_installation_info
	)
	inherited_config = (
		clean_executor.logs_to_file,
		clean_executor.prints_with_substitution,
		clean_executor.prints_banner_on_exit,
		clean_executor.sends_installation_info
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_calls_get_confirmation_message_when_getting_confirmation(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation_message,
	__mock_get_confirmation_keyword
):
	__dummy_test_mode_clean_executor({})._ModeCleanExecutor__get_confirmation()
	__mock_get_confirmation_message.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_get_confirmation_message",
	[pytest.param("confirmation"), pytest.param("another confirmation")],
	indirect=["__mock_get_confirmation_message"]
)
def test_calls_logger_when_getting_confirmation(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation_message,
	__mock_get_confirmation_keyword,
	__mock_logger
):
	__dummy_test_mode_clean_executor({})._ModeCleanExecutor__get_confirmation()
	__mock_logger.assert_called_once_with(__mock_get_confirmation_message())

def test_calls_get_confirmation_keyword_when_getting_confirmation(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation_message,
	__mock_get_confirmation_keyword
):
	__dummy_test_mode_clean_executor({})._ModeCleanExecutor__get_confirmation()
	__mock_get_confirmation_keyword.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_get_confirmation_keyword",
	[pytest.param("keyword 1"), pytest.param("keyword 2")],
	indirect=["__mock_get_confirmation_keyword"]
)
def test_calls_get_user_confirmation_when_getting_confirmation(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation_message,
	__mock_get_confirmation_keyword,
	__mock_get_user_confirmation
):
	__dummy_test_mode_clean_executor({})._ModeCleanExecutor__get_confirmation()
	__mock_get_user_confirmation.assert_called_once_with(__mock_get_confirmation_keyword())

@pytest.mark.parametrize(
	"__mock_get_user_confirmation",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_get_user_confirmation"]
)
def test_returns_expected_confirmation(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation_message,
	__mock_get_confirmation_keyword,
	__mock_get_user_confirmation
):
	confirmation = __dummy_test_mode_clean_executor({})._ModeCleanExecutor__get_confirmation()
	assert (
		confirmation == __mock_get_user_confirmation()
	), get_assertion_message("user confirmation", __mock_get_user_confirmation(), confirmation)

def test_calls_get_confirmation_when_running_executor(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation,
	__mock_get_paths_to_delete
):
	__dummy_test_mode_clean_executor({}).run()
	__mock_get_confirmation.assert_called_once_with()

def test_calls_get_paths_to_delete_when_running_executor(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation,
	__mock_get_paths_to_delete
):
	__dummy_test_mode_clean_executor({}).run()
	__mock_get_paths_to_delete.assert_called_once_with()

def test_calls_delete_paths_to_delete_when_running_executor(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_delete_paths
):
	__dummy_test_mode_clean_executor({}).run()
	__mock_delete_paths.assert_called_once_with(__mock_get_paths_to_delete())

def test_calls_logger_when_running_executor(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_logger,
	__mock_get_done_message
):
	__dummy_test_mode_clean_executor({}).run()
	__mock_logger.assert_called_once_with(
		__mock_get_done_message()
	)

@pytest.mark.parametrize(
	"__mock_get_confirmation",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_get_confirmation"]
)
def test_returns_expected_values_when_running_executor(
	__dummy_test_mode_clean_executor,
	__mock_get_confirmation,
	__mock_get_paths_to_delete
):
	expected_values = (0, "") if __mock_get_confirmation() else (errors.INTERRUPTED_ERROR, "")
	values = __dummy_test_mode_clean_executor({}).run()
	assert (
		values == expected_values
	), get_assertion_message("return values", expected_values, values)

@pytest.fixture
def __no_implementation_child():
	class DummyModeExecutor(ModeCleanExecutor):
		pass
	return DummyModeExecutor

@pytest.fixture
def __dummy_test_mode_clean_executor():
	class TestExecutor(ModeCleanExecutor):
		def _get_paths_to_delete(self):
			return []
		def _get_confirmation_message(self):
			return ""
		def _get_confirmation_keyword(self):
			return ""
	# For coverage
	executor = TestExecutor({})
	executor._get_paths_to_delete()
	executor._get_confirmation_message()
	executor._get_confirmation_keyword()
	return TestExecutor

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return 0, ""
	TestExecutor({}).run() # For coverage
	return TestExecutor

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(params=["confirmation message"])
def __mock_get_confirmation_message(__dummy_test_mode_clean_executor, request):
	with patch.object(__dummy_test_mode_clean_executor, "_get_confirmation_message") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True, params=[True])
def __mock_get_user_confirmation(request):
	with patch(
		"xmipp3_installer.application.user_interactions.get_user_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=["YES"])
def __mock_get_confirmation_keyword(__dummy_test_mode_clean_executor, request):
	with patch.object(__dummy_test_mode_clean_executor, "_get_confirmation_keyword") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[True])
def __mock_get_confirmation(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_clean.mode_clean_executor.ModeCleanExecutor._ModeCleanExecutor__get_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(params=[["path1"]])
def __mock_get_paths_to_delete(__dummy_test_mode_clean_executor, request):
	with patch.object(__dummy_test_mode_clean_executor, "_get_paths_to_delete") as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_delete_paths():
	with patch(
		"xmipp3_installer.shared.file_operations.delete_paths"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_done_message():
	with patch(
		"xmipp3_installer.application.logger.predefined_messages.get_done_message"
	) as mock_method:
		mock_method.return_value = "Done message"
		yield mock_method
