from unittest.mock import patch

import pytest

from xmipp3_installer.application.logger import predefined_messages
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.tmp import versions

from .... import get_assertion_message

__SECTION_MESSAGE_LEN = 10
__BRANCH_NAME = "devel"
__TAG_VERSION = "tag-version"

def test_calls_logger_green_when_getting_done_message(__mock_logger_green):
  predefined_messages.get_done_message()
  __mock_logger_green.assert_called_once_with("Done")

def test_returns_expected_done_message(__mock_logger_green):
  done_message = predefined_messages.get_done_message()
  expected_done_message = __mock_logger_green("Done")
  assert (
    done_message == expected_done_message
  ), get_assertion_message("done message", expected_done_message, done_message)

def test_calls_logger_yellow_when_getting_working_message(__mock_logger_yellow):
  predefined_messages.get_working_message()
  __mock_logger_yellow.assert_called_once_with("Working...")

def test_returns_expected_working_message(__mock_logger_yellow):
  working_message = predefined_messages.get_working_message()
  expected_working_message = __mock_logger_yellow("Working...")
  assert (
    working_message == expected_working_message
  ), get_assertion_message("working message", expected_working_message, working_message)

@pytest.mark.parametrize(
  "__mock_section_message_len,input_text,expected_text",
  [
    pytest.param(0, "A", "A"),
    pytest.param(1, "A", "A"),
    pytest.param(4, "A", "A"),
    pytest.param(5, "A", "- A -"),
    pytest.param(6, "A", "-- A -"),
    pytest.param(7, "A", "-- A --")
  ],
  indirect=["__mock_section_message_len"]
)
def test_returns_expected_section_message(
  __mock_section_message_len,
  input_text,
  expected_text
):
  section_message = predefined_messages.get_section_message(input_text)
  assert (
    section_message == expected_text
  ), get_assertion_message("section message", expected_text, section_message)

def test_calls_is_tag_when_getting_success_message(
  __mock_is_tag,
  __mock_get_current_branch
):
  predefined_messages.get_success_message()
  __mock_is_tag.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_is_tag,expected_call_number",
  [
    pytest.param(False, 1),
    pytest.param(True, 0)
  ],
  indirect=["__mock_is_tag"]
)
def test_calls_get_current_branch_when_getting_success_message_only_if_is_not_tag(
  __mock_is_tag,
  expected_call_number,
  __mock_get_current_branch
):
  predefined_messages.get_success_message()
  assert (
    __mock_get_current_branch.call_count == expected_call_number
  ), get_assertion_message("get current branch call count", expected_call_number, __mock_get_current_branch.call_count)

@pytest.mark.parametrize(
  "__mock_is_tag,expected_release_name",
  [
    pytest.param(False, __BRANCH_NAME),
    pytest.param(True, __TAG_VERSION)
  ],
  indirect=["__mock_is_tag"]
)
def test_calls_logger_green_when_getting_success_message(
  __mock_is_tag,
  expected_release_name,
  __mock_get_current_branch,
  __mock_logger_green
):
  predefined_messages.get_success_message()
  __mock_logger_green.assert_called_once_with(
    f'Xmipp {expected_release_name} has been successfully installed, enjoy it!'
  )

@pytest.mark.parametrize(
  "__mock_is_tag,expected_release_name",
  [
    pytest.param(False, __BRANCH_NAME),
    pytest.param(True, __TAG_VERSION)
  ],
  indirect=["__mock_is_tag"]
)
def test_returns_expected_success_message(
  __mock_is_tag,
  expected_release_name,
  __mock_get_current_branch,
  __mock_logger_green
):
  success_message = predefined_messages.get_success_message()
  inner_message = f"Xmipp {expected_release_name} has been successfully installed, enjoy it!"
  line_len = len(f' {inner_message} ')
  expected_success_message = '\n'.join([
    "",
    f"*{'*' * line_len}*",
    f"*{' ' * line_len}*",
    f"* {__mock_logger_green(inner_message)} *",
    f"*{' ' * line_len}*",
    f"*{'*' * line_len}*"
  ])
  assert (
    success_message == expected_success_message
  ), get_assertion_message("success message", expected_success_message, success_message)

@pytest.fixture
def __mock_logger_green():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.green"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"green-{text}-green"
    yield mock_method

@pytest.fixture
def __mock_logger_yellow():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.yellow"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
    yield mock_method

@pytest.fixture(params=[__SECTION_MESSAGE_LEN])
def __mock_section_message_len(request):
  with patch.object(predefined_messages, "__SECTION_MESSAGE_LEN", new=request.param):
    yield request.param

@pytest.fixture(params=[False])
def __mock_is_tag(request):
  with patch(
    "xmipp3_installer.installer.handlers.git_handler.is_tag"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_get_current_branch():
  with patch(
    "xmipp3_installer.installer.handlers.git_handler.get_current_branch"
  ) as mock_method:
    mock_method.return_value = __BRANCH_NAME
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_xmipp_versions():
  with patch.object(versions, "XMIPP_VERSIONS", new={'key1': {'key2': __TAG_VERSION}}):
    with patch.object(constants, "XMIPP", new="key1"):
      with patch.object(versions, "VERSION_KEY", new="key2"):
        yield __TAG_VERSION
