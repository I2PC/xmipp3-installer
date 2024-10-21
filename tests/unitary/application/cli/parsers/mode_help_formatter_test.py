from typing import List
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.mode_help_formatter import ModeHelpFormatter
from xmipp3_installer.application.cli import arguments

from .... import get_assertion_message

__PROGRAM_NAME = "test-program"
__INNER_KEY = "key"
__PARAMS = {
	"param1": { __INNER_KEY: "test1" },
	"param2": { __INNER_KEY: "test2" }
}
__MODE_EXAMPLES = {
	"mode1": ["mode1-test1", "mode1-test2"],
	"mode2": ["mode2-test"],
	"mode3": []
}
__MODE_ARGS = {
	"mode1": ["mode1-arg1"],
	"mode2": []
}

@pytest.mark.parametrize(
	"__mock_formatter_prog,expected_mode",
	[
		pytest.param("the test mode is all", "all"),
		pytest.param("now the mode is new", "new"),
		pytest.param("mode", "mode")
	],
	indirect=["__mock_formatter_prog"]
)
def test_get_mode(
	expected_mode,
	__mock_formatter_prog
):
	mode = __mock_formatter_prog._ModeHelpFormatter__get_mode()
	assert (
		mode == expected_mode
	), get_assertion_message("mode", expected_mode, mode)

@pytest.mark.parametrize(
	"args,expected_contains",
	[
		pytest.param(["mandatory", "--optional"], True),
		pytest.param(["optional", "optional2"], False),
		pytest.param(["-mandatory"], True)
	],
)
def test_checks_if_args_contain_optional(
	args,
	expected_contains,
	__setup_formatter
):
	contains = __setup_formatter._ModeHelpFormatter__args_contain_optional(args)
	assert (
		contains == expected_contains
	), get_assertion_message("optional arg check result", expected_contains, contains)

@pytest.mark.parametrize(
	"args,expected_arg_info",
	[
		pytest.param(
			["param1", "param2"],
			"\tparam1-1, param1-2test1\tparam2-1, param2-2test2"
		),
		pytest.param([], "")
	],
)
def test_returns_expected_args_info(
	args,
	expected_arg_info,
	__mock_params,
	__mock_description,
	__mock_get_param_names,
	__mock_text_with_limits,
	__setup_formatter
):
	args_info = __setup_formatter._ModeHelpFormatter__get_args_info(args)
	assert (
		args_info == expected_arg_info
	), get_assertion_message("args info", expected_arg_info, args_info)

def test_calls_text_with_limits_with_expected_params_when_getting_arg_info(
	__mock_params,
	__mock_description,
	__mock_get_param_names,
	__mock_text_with_limits,
	__setup_formatter
):
	params = ["param1"]
	__setup_formatter._ModeHelpFormatter__get_args_info(params)
	__mock_text_with_limits.assert_called_once_with(
		f"\t{params[0]}-1, {params[0]}-2",
		__PARAMS[params[0]][__INNER_KEY]
	)

def test_calls_get_param_names_with_expected_params_when_getting_arg_info(
	__mock_params,
	__mock_description,
	__mock_get_param_names,
	__mock_text_with_limits,
	__setup_formatter
):
	params = ["param1"]
	__setup_formatter._ModeHelpFormatter__get_args_info(params)
	__mock_get_param_names.assert_called_once_with(params[0])

@pytest.mark.parametrize(
	"mode,expected_message",
	[
		pytest.param(
			"mode1",
			"\nExample 1: mode1-test1\nExample 2: mode1-test2\n"
		),
		pytest.param("mode2", "\nExample: mode2-test\n"),
		pytest.param("mode3", "")
	],
)
def test_returns_expected_examples_message(
	mode,
	expected_message,
	__mock_mode_examples,
	__setup_formatter
):
	examples_message = __setup_formatter._ModeHelpFormatter__get_examples_message(mode)
	assert (
		examples_message == expected_message
	), get_assertion_message("examples message", expected_message, examples_message)

def test_calls_get_param_first_name(
	__mock_mode_args,
	__mock_xmipp_program_name,
	__mock_get_param_first_name,
	__mock_args_contain_optional,
	__mock_logger_yellow,
	__mock_get_help_separator,
	__mock_get_args_info,
	__setup_formatter
):
	mode = "mode1"
	__setup_formatter._ModeHelpFormatter__get_args_message(mode)
	__mock_get_param_first_name.assert_called_once_with(
		__MODE_ARGS[mode][0]
	)

def test_does_not_call_get_param_first_name(
	__mock_mode_args,
	__mock_xmipp_program_name,
	__mock_get_param_first_name,
	__mock_args_contain_optional,
	__mock_logger_yellow,
	__mock_get_help_separator,
	__mock_get_args_info,
	__setup_formatter
):
	mode = "mode2"
	__setup_formatter._ModeHelpFormatter__get_args_message(mode)
	__mock_get_param_first_name.assert_not_called()

@pytest.fixture
def __setup_formatter():
	yield ModeHelpFormatter("test")

@pytest.fixture
def __mock_formatter_prog(request, __setup_formatter):
	mode = request.param if hasattr(request, "param") else "this is the mode: default_mode"
	with patch.object(__setup_formatter, "_prog", mode):
		yield __setup_formatter

@pytest.fixture
def __mock_params():
	with patch.object(arguments, "PARAMS", __PARAMS):
		yield

@pytest.fixture
def __mock_description():
	with patch.object(arguments, "DESCRIPTION", __INNER_KEY):
		yield

@pytest.fixture
def __mock_get_param_names():
	with patch(
		"xmipp3_installer.application.cli.parsers.format.get_param_names"
	) as mock_method:
		def __return_in_list(arg: str) -> List[str]:
			return [f"{arg}-1", f"{arg}-2"]
		mock_method.side_effect = __return_in_list
		yield mock_method

@pytest.fixture
def __mock_text_with_limits():
	with patch(
		"xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._text_with_limits"
	) as mock_method:
		def __append_text(original: str, appended: str) -> str:
			return f"{original}{appended}"
		mock_method.side_effect = __append_text
		yield mock_method

@pytest.fixture
def __mock_mode_examples():
	with patch.object(arguments, "MODE_EXAMPLES", __MODE_EXAMPLES):
		yield

@pytest.fixture
def __mock_mode_args():
	with patch.object(arguments, "MODE_ARGS", __MODE_ARGS):
		yield

@pytest.fixture
def __mock_xmipp_program_name():
	with patch.object(arguments, "XMIPP_PROGRAM_NAME", __PROGRAM_NAME):
		yield

@pytest.fixture
def __mock_get_param_first_name():
	with patch(
		"xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._get_param_first_name"
	) as mock_method:
		def __get_name(arg_name: str) -> str:
			return f"{arg_name}-name"
		mock_method.side_effect = __get_name
		yield mock_method

@pytest.fixture
def __mock_args_contain_optional(request):
	with patch(
		"xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._ModeHelpFormatter__args_contain_optional"
	) as mock_method:
		mock_method.return_value = request.param if hasattr(request, "param") else False
		yield mock_method

@pytest.fixture
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		def __return_with_afixes(text):
			return f"format-start-{text}-format-end"
		mock_method.side_effect = __return_with_afixes
		yield mock_method

@pytest.fixture
def __mock_get_help_separator():
	with patch(
		"xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._get_help_separator"
	) as mock_method:
		mock_method.return_value = '_____'
		yield mock_method

@pytest.fixture
def __mock_get_args_info():
	with patch(
		"xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._ModeHelpFormatter__get_args_info"
	) as mock_method:
		def __get_info(args: List[str]) -> str:
			return f'info-{"_".join(args)}-info'
		mock_method.side_effect = __get_info
		yield mock_method
