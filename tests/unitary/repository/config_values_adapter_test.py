from unittest.mock import patch

import pytest

from xmipp3_installer.repository.config_vars import default_values, variables
from xmipp3_installer.repository.config_vars import config_values_adapter

from ... import get_assertion_message

__TOGGLE_KEY = variables.SEND_INSTALLATION_STATISTICS
__NON_TOGGLE_KEY = variables.CC_FLAGS
__UNKNOWN_KEY = "mykey"
__NON_TOGGLE_VALUE = "whatever"
__CONVERTED_VALUE = "converted_value"
__INPUT_CONTEXT_VALUES = {
  variables.SEND_INSTALLATION_STATISTICS: False,
  variables.CUDA: __NON_TOGGLE_VALUE,
  variables.CMAKE: __NON_TOGGLE_VALUE
}
__OUTPUT_FILE_VALUES = {
  variables.SEND_INSTALLATION_STATISTICS: default_values.OFF,
  variables.CUDA: default_values.CONFIG_DEFAULT_VALUES[variables.CUDA],
  variables.CMAKE: __NON_TOGGLE_VALUE
}
__INPUT_FILE_VALUES = {
  variables.SEND_INSTALLATION_STATISTICS: default_values.ON,
  variables.CUDA: __NON_TOGGLE_VALUE,
  variables.CMAKE: __NON_TOGGLE_VALUE
}
__OUTPUT_CONTEXT_VALUES = {
  variables.SEND_INSTALLATION_STATISTICS: True,
  variables.CUDA: default_values.CONFIG_DEFAULT_VALUES[variables.CUDA] == default_values.ON,
  variables.CMAKE: __NON_TOGGLE_VALUE
}

@pytest.mark.parametrize(
  "input_value,expected_value",
  [
    pytest.param(True, default_values.ON),
    pytest.param(False, default_values.OFF)
  ]
)
def test_returns_expected_string_from_boolean(input_value, expected_value):
  value = config_values_adapter.__get_string_value_from_boolean(input_value)
  assert (
    value == expected_value
  ), get_assertion_message("boolean to string value", expected_value, value)

@pytest.mark.parametrize(
  "input_key,input_value,expected_value",
  [
    pytest.param(__TOGGLE_KEY, default_values.ON, True),
    pytest.param(__NON_TOGGLE_KEY, default_values.ON, True),
    pytest.param(__TOGGLE_KEY, default_values.OFF, False),
    pytest.param(__NON_TOGGLE_KEY, default_values.OFF, False),
    pytest.param(
      __TOGGLE_KEY,
      __NON_TOGGLE_VALUE,
      default_values.CONFIG_DEFAULT_VALUES[__TOGGLE_KEY] == default_values.ON),
    pytest.param(
      __NON_TOGGLE_KEY,
      __NON_TOGGLE_VALUE,
      default_values.CONFIG_DEFAULT_VALUES[__NON_TOGGLE_KEY] == default_values.ON),
  ]
)
def test_returns_expected_boolean_from_string(input_key, input_value, expected_value):
  value = config_values_adapter.__get_boolean_value_from_string(input_key, input_value, False)
  assert (
    value == expected_value
  ), get_assertion_message("string to boolean value", expected_value, value)

def test_calls_logger_when_toggle_key_has_unrecognized_value_and_show_error_is_true_while_converting_from_string_to_boolean(
  __mock_logger,
  __mock_logger_yellow
):
  config_values_adapter.__get_boolean_value_from_string(__TOGGLE_KEY, __NON_TOGGLE_VALUE, True)
  __mock_logger.assert_called_once_with(
    __mock_logger_yellow(
      f"WARNING: config variable '{__TOGGLE_KEY}' has unrecognized value '{__NON_TOGGLE_VALUE}'. "
      f"Toggle values must be either '{default_values.ON}' or '{default_values.OFF}'. "
      f"Default value '{default_values.CONFIG_DEFAULT_VALUES[__TOGGLE_KEY]}' will be used instead."
    )
  )

def test_does_not_call_logger_when_toggle_key_has_unrecognized_value_and_show_error_is_false_while_converting_from_string_to_boolean(
  __mock_logger
):
  config_values_adapter.__get_boolean_value_from_string(__TOGGLE_KEY, __NON_TOGGLE_VALUE, False)
  __mock_logger.assert_not_called()

def test_raises_key_error_when_unknown_key_has_unrecognized_value_while_converting_from_string_to_boolean():
  with pytest.raises(KeyError):
    config_values_adapter.__get_boolean_value_from_string(__UNKNOWN_KEY, __NON_TOGGLE_VALUE, False)

@pytest.mark.parametrize(
  "key, value, expected_value",
  [
    pytest.param(__NON_TOGGLE_KEY, __NON_TOGGLE_VALUE, __NON_TOGGLE_VALUE),
    pytest.param(__NON_TOGGLE_KEY, True, True),
    pytest.param(__TOGGLE_KEY, __NON_TOGGLE_VALUE, __CONVERTED_VALUE),
    pytest.param(__TOGGLE_KEY, True, __CONVERTED_VALUE)
  ]
)
def test_returns_expected_file_value_from_context_value(
  key,
  value,
  expected_value,
  __mock_get_string_value_from_boolean
):
  converted_value = config_values_adapter.__get_file_value_from_context_value(
    key,
    value
  )
  assert (
    converted_value == expected_value
  ), get_assertion_message("context to file value", expected_value, converted_value)

@pytest.mark.parametrize(
  "key, value, expected_value",
  [
    pytest.param(__NON_TOGGLE_KEY, __NON_TOGGLE_VALUE, __NON_TOGGLE_VALUE),
    pytest.param(__NON_TOGGLE_KEY, True, True),
    pytest.param(__TOGGLE_KEY, __NON_TOGGLE_VALUE, __CONVERTED_VALUE),
    pytest.param(__TOGGLE_KEY, True, __CONVERTED_VALUE)
  ]
)
def test_returns_expected_context_value_from_file_value(
  key,
  value,
  expected_value,
  __mock_get_boolean_value_from_string
):
  converted_value = config_values_adapter.__get_context_value_from_file_value(
    key,
    value,
    False
  )
  assert (
    converted_value == expected_value
  ), get_assertion_message("file to context value", expected_value, converted_value)

def test_returns_expected_file_values_from_context_values():
  file_values = config_values_adapter.get_file_values_from_context_values(__INPUT_CONTEXT_VALUES)
  assert (
    file_values == __OUTPUT_FILE_VALUES
  ), get_assertion_message("converted file values", __OUTPUT_FILE_VALUES, file_values)

def test_returns_expected_context_values_from_file_values():
  context_values = config_values_adapter.get_context_values_from_file_values(__INPUT_FILE_VALUES)
  assert (
    context_values == __OUTPUT_CONTEXT_VALUES
  ), get_assertion_message("converted context values", __OUTPUT_CONTEXT_VALUES, context_values)

@pytest.fixture(autouse=True)
def __mock_logger():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.__call__"
  ) as mock_method:
    yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.yellow"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
    yield mock_method

@pytest.fixture
def __mock_get_string_value_from_boolean():
  with patch(
    "xmipp3_installer.repository.config_vars.config_values_adapter.__get_string_value_from_boolean"
  ) as mock_method:
    mock_method.return_value = __CONVERTED_VALUE
    yield mock_method

@pytest.fixture
def __mock_get_boolean_value_from_string():
  with patch(
    "xmipp3_installer.repository.config_vars.config_values_adapter.__get_boolean_value_from_string"
  ) as mock_method:
    mock_method.return_value = __CONVERTED_VALUE
    yield mock_method
