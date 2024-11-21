from unittest.mock import patch

import pytest

from xmipp3_installer.repository.invalid_config_line import InvalidConfigLineError

from ... import get_assertion_message

def test_checks_if_exception_is_instance_of_runtime_error():
	invalid_line_error = InvalidConfigLineError()
	assert (
		isinstance(invalid_line_error, RuntimeError)
	), get_assertion_message("exception class", RuntimeError, type(invalid_line_error))

@pytest.mark.parametrize(
	"config_file,line_number,line",
	[
		pytest.param("test-file", 1, "test line"),
		pytest.param("other-test-file", 5, "other test line"),
  ]
)
def test_returns_expected_message_when_generating_error_message(
	config_file,
	line_number,
	line,
	__mock_logger_yellow,
	__mock_logger_red
):
	error_message = InvalidConfigLineError.generate_error_message(
		config_file,
		line_number,
		line
  )
	expected_message = '\n'.join([
    __mock_logger_yellow(f"WARNING: There was an error parsing {config_file} file: "),
    __mock_logger_red(f'Unable to parse line {line_number}: {line}'),
    __mock_logger_yellow(
      "Contents of config file won't be read, default values will be used instead.\n"
      "You can create a new file template from scratch running './xmipp config -o'."
    )
    ])
	assert (
		error_message == expected_message
  ), get_assertion_message("exception error message", expected_message, error_message)

@pytest.fixture
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"yellow-start-{text}-yellow-end"
		yield mock_method

@pytest.fixture
def __mock_logger_red():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.red"
	) as mock_method:
		mock_method.side_effect = lambda text: f"red-start-{text}-red-end"
		yield mock_method
