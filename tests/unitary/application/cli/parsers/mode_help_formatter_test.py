from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli.parsers.mode_help_formatter import ModeHelpFormatter
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.application.cli.arguments import modes, params

from ..... import get_assertion_message

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
__NOTE_MESSAGE = "Note: only params starting with '-' are optional. The rest are required.\n"

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

def test_calls_get_param_first_name_when_getting_args_message(
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

def test_does_not_call_get_param_first_name_when_getting_args_message(
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

def test_calls_args_contain_optional_when_getting_args_message(
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
  __mock_args_contain_optional.assert_called_once_with(
    [__mock_get_param_first_name(__MODE_ARGS[mode][0])]
  )

def test_calls_logger_yellow_when_getting_args_message(
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
  __mock_args_contain_optional.return_value = True
  __setup_formatter._ModeHelpFormatter__get_args_message(mode)
  __mock_logger_yellow.assert_called_once_with(__NOTE_MESSAGE)

@pytest.mark.parametrize(
  "mode,__mock_args_contain_optional",
  [
    pytest.param("mode1", False),
    pytest.param("mode2", False),
    pytest.param("mode2", True)
  ],
  indirect=["__mock_args_contain_optional"]
)
def test_does_not_call_logger_yellow_when_getting_args_message(
  mode,
  __mock_mode_args,
  __mock_xmipp_program_name,
  __mock_get_param_first_name,
  __mock_args_contain_optional,
  __mock_logger_yellow,
  __mock_get_help_separator,
  __mock_get_args_info,
  __setup_formatter
):
  __setup_formatter._ModeHelpFormatter__get_args_message(mode)
  __mock_logger_yellow.assert_not_called()

def test_does_not_call_get_help_separator_when_getting_args_message(
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
  __mock_get_help_separator.assert_not_called()

@pytest.mark.parametrize(
  "mode",
  [pytest.param("mode1"), pytest.param("mode2")],
)
def test_calls_get_args_info_when_getting_args_message(
  mode,
  __mock_mode_args,
  __mock_xmipp_program_name,
  __mock_get_param_first_name,
  __mock_args_contain_optional,
  __mock_logger_yellow,
  __mock_get_help_separator,
  __mock_get_args_info,
  __setup_formatter
):
  __setup_formatter._ModeHelpFormatter__get_args_message(mode)
  __mock_get_args_info.assert_called_once_with(__MODE_ARGS[mode])

@pytest.mark.parametrize(
  "mode,__mock_args_contain_optional",
  [
    pytest.param("mode1", False),
    pytest.param("mode1", True),
    pytest.param("mode2", False),
    pytest.param("mode2", True)
  ],
  indirect=["__mock_args_contain_optional"]
)
def test_returns_expected_args_message(
  mode,
  __mock_mode_args,
  __mock_xmipp_program_name,
  __mock_get_param_first_name,
  __mock_args_contain_optional,
  __mock_logger_yellow,
  __mock_get_help_separator,
  __mock_get_args_info,
  __setup_formatter
):
  expected_help_message = __get_args_help_message(
    mode,
    __mock_args_contain_optional.return_value,
    __setup_formatter,
    __mock_logger_yellow,
    __mock_get_args_info
  )
  help_message = __setup_formatter._ModeHelpFormatter__get_args_message(mode)
  assert (
    help_message == expected_help_message
  ), get_assertion_message("args help message", expected_help_message, help_message)

def test_calls_get_mode_when_formatting_help(
  __mock_get_mode,
  __mock_get_mode_help,
  __mock_get_args_message,
  __mock_get_examples_message,
  __mock_get_formatting_tabs,
  __setup_formatter
):
  __setup_formatter.format_help()
  __mock_get_mode.assert_called_once_with()

def test_calls_get_mode_help_when_formatting_help(
  __mock_get_mode,
  __mock_get_mode_help,
  __mock_get_args_message,
  __mock_get_examples_message,
  __mock_get_formatting_tabs,
  __setup_formatter
):
  __setup_formatter.format_help()
  __mock_get_mode_help.assert_called_once_with(__mock_get_mode(), general=False)

def test_calls_get_args_message_when_formatting_help(
  __mock_get_mode,
  __mock_get_mode_help,
  __mock_get_args_message,
  __mock_get_examples_message,
  __mock_get_formatting_tabs,
  __setup_formatter
):
  __setup_formatter.format_help()
  __mock_get_args_message.assert_called_once_with(__mock_get_mode())

def test_calls_get_examples_message_when_formatting_help(
  __mock_get_mode,
  __mock_get_mode_help,
  __mock_get_args_message,
  __mock_get_examples_message,
  __mock_get_formatting_tabs,
  __setup_formatter
):
  __setup_formatter.format_help()
  __mock_get_examples_message.assert_called_once_with(__mock_get_mode())

def test_returns_expected_help_message_when_formatting_help(
  __mock_get_mode,
  __mock_get_mode_help,
  __mock_get_args_message,
  __mock_get_examples_message,
  __mock_get_formatting_tabs,
  __setup_formatter
):
  formatted_help = __setup_formatter.format_help()
  mode = __mock_get_mode()
  expected_formatted_help = ''.join([
    f"{__mock_get_mode_help(mode, general=False)}\n\n",
    __mock_get_args_message(mode),
    __mock_get_examples_message(mode)
  ])
  expected_formatted_help = __mock_get_formatting_tabs(expected_formatted_help)
  assert (
    formatted_help == expected_formatted_help
  ), get_assertion_message("formatted help", expected_formatted_help, formatted_help)

def __get_args_help_message(
  mode: str,
  contains_optional: bool,
  formatter: ModeHelpFormatter,
  logger_yellow,
  get_args_info
) -> str:
  args = __MODE_ARGS[mode]
  exist_args = len(args) > 0
  return ''.join([
    logger_yellow(__NOTE_MESSAGE) if exist_args > 0 and contains_optional else "",
    f"Usage: {arguments.XMIPP_PROGRAM_NAME} {mode}",
    f"{' [options]' if len(args) > 0 else ''}\n",
    f"{formatter._get_help_separator()}\t# Options #\n\n" if exist_args else "",
    get_args_info(args)
  ])

@pytest.fixture
def __setup_formatter():
  yield ModeHelpFormatter("test")

@pytest.fixture(params=["this is the mode: default_mode"])
def __mock_formatter_prog(request, __setup_formatter):
  with patch.object(__setup_formatter, "_prog", request.param):
    yield __setup_formatter

@pytest.fixture
def __mock_params():
  with patch.object(params, "PARAMS", __PARAMS):
    yield

@pytest.fixture
def __mock_description():
  with patch.object(params, "DESCRIPTION", __INNER_KEY):
    yield

@pytest.fixture
def __mock_get_param_names():
  with patch(
    "xmipp3_installer.application.cli.parsers.format.get_param_names"
  ) as mock_method:
    mock_method.side_effect = lambda arg: [f"{arg}-1", f"{arg}-2"]
    yield mock_method

@pytest.fixture
def __mock_text_with_limits():
  with patch(
    "xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._text_with_limits"
  ) as mock_method:
    mock_method.side_effect = lambda original, appended: f"{original}{appended}"
    yield mock_method

@pytest.fixture
def __mock_mode_examples():
  with patch.object(modes, "MODE_EXAMPLES", __MODE_EXAMPLES):
    yield

@pytest.fixture
def __mock_mode_args():
  with patch.object(modes, "MODE_ARGS", __MODE_ARGS):
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
    mock_method.side_effect = lambda arg_name: f"{arg_name}-name"
    yield mock_method

@pytest.fixture(params=[False])
def __mock_args_contain_optional(request):
  with patch(
    "xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._ModeHelpFormatter__args_contain_optional"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_logger_yellow():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.yellow"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"format-start-{text}-format-end"
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
    mock_method.side_effect = lambda args: f'info-{"_".join(args)}-info'
    yield mock_method

@pytest.fixture
def __mock_get_mode():
  with patch(
    "xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._ModeHelpFormatter__get_mode"
  ) as mock_method:
    mock_method.return_value = "mode1"
    yield mock_method

@pytest.fixture
def __mock_get_mode_help():
  with patch(
    "xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._get_mode_help"
  ) as mock_method:
    mock_method.side_effect = lambda mode, general=False: f"help-{mode}-{general}-help"
    yield mock_method

@pytest.fixture
def __mock_get_args_message():
  with patch(
    "xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._ModeHelpFormatter__get_args_message"
  ) as mock_method:
    mock_method.side_effect = lambda mode: f"args_message-{mode}-args_message"
    yield mock_method

@pytest.fixture
def __mock_get_examples_message():
  with patch(
    "xmipp3_installer.application.cli.parsers.mode_help_formatter.ModeHelpFormatter._ModeHelpFormatter__get_examples_message"
  ) as mock_method:
    mock_method.side_effect = lambda mode: f"examples_message-{mode}-examples_message"
    yield mock_method

@pytest.fixture
def __mock_get_formatting_tabs():
  with patch(
    "xmipp3_installer.application.cli.parsers.format.get_formatting_tabs"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"format_start - {text} - format_end"
    yield mock_method
