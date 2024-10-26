import os
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.error_handler_parser import ErrorHandlerArgumentParser

from ..... import get_assertion_message

__FORMATTED_HELP = "This is the formatted help"

@pytest.mark.parametrize(
	"args,expected_is_generic",
	[
		pytest.param([], False),
		pytest.param(["arg1"], False),
		pytest.param(["arg1", "arg2"], True),
		pytest.param(["arg1", "arg2", "arg3"], True)
	],
)
def test_checks_is_mode_generic(
	args,
	expected_is_generic,
	__setup_parser
):
	is_generic = __setup_parser._ErrorHandlerArgumentParser__is_mode_generic(args)
	assert (
		is_generic == expected_is_generic
	), get_assertion_message("result", expected_is_generic, is_generic)

@pytest.mark.parametrize(
	"args,expected_mode",
	[
		pytest.param(["arg1"], "arg1"),
		pytest.param(["arg1", "arg2"], "arg2"),
		pytest.param(["arg1", "arg2", "arg3"], "arg3")
	],
)
def test_gets_expected_mode(
	args,
	expected_mode,
	__setup_parser
):
	mode = __setup_parser._ErrorHandlerArgumentParser__get_mode(args)
	assert (
		mode == expected_mode
	), get_assertion_message("mode", expected_mode, mode)

@pytest.mark.parametrize(
	"__mock_formatter_prog,expected_args",
	[
		pytest.param("", [""]),
		pytest.param("arg1", ["arg1"]),
		pytest.param("arg1 arg2", ["arg1", "arg2"]),
		pytest.param("test test2 test3", ["test", "test2", "test3"])
	],
	indirect=["__mock_formatter_prog"]
)
def test_gets_expected_args(
	__mock_formatter_prog,
	expected_args
):
	args = __mock_formatter_prog._ErrorHandlerArgumentParser__get_args()
	assert (
		args == expected_args
	), get_assertion_message("mode", expected_args, args)

def test_exits_when_getting_error_message(
	__mock_get_args,
	__mock_logger_red,
	__mock_stdout_stderr,
	__setup_parser
):
	with pytest.raises(SystemExit):
		__setup_parser.error("test-error-message")

@pytest.mark.parametrize(
	"__mock_get_args,expected_args,expected_line_break,expected_mode",
	[
		pytest.param(["arg1"], __FORMATTED_HELP, "", "arg1"),
		pytest.param([""], __FORMATTED_HELP, "", ""),
		pytest.param(["arg1", "arg2"], "arg1", "\n", "arg2"),
		pytest.param(["arg1", "arg2", "arg3"], "arg1 arg2", "\n", "arg3")
	],
	indirect=["__mock_get_args"]
)
def test_gets_expected_error_message(
	__mock_get_args,
	expected_args,
	expected_line_break,
	expected_mode,
	__mock_format_help,
	__mock_logger_red,
	__mock_get_formatting_tabs,
	__mock_exit,
	__setup_parser
):
	external_error_message = "test-error-message"
	custom_error_message = __format_red(f"{expected_mode}: error: {external_error_message}\n")
	__setup_parser.error(external_error_message)
	__mock_exit.assert_called_once_with(
		1,
		__format_tabs(f"{expected_args}{expected_line_break}{custom_error_message}")
	)

def __format_red(text: str) -> str:
	return f"red_start-{text}-red_end"

def __format_tabs(text: str) -> str:
	return f"tabs_start-{text}-tabs_end"

@pytest.fixture
def __setup_parser():
	return ErrorHandlerArgumentParser("test")

@pytest.fixture
def __mock_formatter_prog(request, __setup_parser):
	args = request.param if hasattr(request, "param") else "this are the default args"
	with patch.object(__setup_parser, "prog", args):
		yield __setup_parser

@pytest.fixture
def __mock_get_args(request):
	with patch(
		"xmipp3_installer.application.cli.parsers.error_handler_parser.ErrorHandlerArgumentParser._ErrorHandlerArgumentParser__get_args"
	) as mock_method:
		mock_method.return_value = request.param if hasattr(request, "param") else ["arg1"]
		yield mock_method

@pytest.fixture
def __mock_format_help():
	with patch(
		"xmipp3_installer.application.cli.parsers.error_handler_parser.ErrorHandlerArgumentParser.format_help"
	) as mock_method:
		mock_method.return_value = __FORMATTED_HELP
		yield mock_method

@pytest.fixture
def __mock_logger_red():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.red"
	) as mock_method:
		mock_method.side_effect = __format_red
		yield mock_method

@pytest.fixture
def __mock_get_formatting_tabs():
	with patch(
		"xmipp3_installer.application.cli.parsers.format.get_formatting_tabs"
	) as mock_method:
		mock_method.side_effect = __format_tabs
		yield mock_method

@pytest.fixture
def __mock_exit():
	with patch(
		"xmipp3_installer.application.cli.parsers.error_handler_parser.ErrorHandlerArgumentParser.exit"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_stdout_stderr():
	with patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w')), \
	patch('sys.stderr', new_callable=lambda: open(os.devnull, 'w')):
		yield
