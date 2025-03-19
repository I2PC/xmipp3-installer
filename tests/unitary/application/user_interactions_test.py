from unittest.mock import patch

import pytest

from xmipp3_installer.application import user_interactions

from ... import get_assertion_message

__CONFIRMATION_TEXT = "YeS"

def test_calls_input_when_getting_user_confirmation(__mock_input):
  user_interactions.get_user_confirmation(__CONFIRMATION_TEXT)
  __mock_input.assert_called_once_with()

@pytest.mark.parametrize(
  "__mock_input,case_sensitive,expected_confirmation",
  [
    pytest.param("no", False, False),
    pytest.param("no", True, False),
    pytest.param("yes", False, True),
    pytest.param("yes", True, False),
    pytest.param(__CONFIRMATION_TEXT, False, True),
    pytest.param(__CONFIRMATION_TEXT, True, True)
  ],
  indirect=["__mock_input"]
)
def test_returns_expected_user_confirmation(
  __mock_input,
  case_sensitive,
  expected_confirmation
):
  confirmation = user_interactions.get_user_confirmation(
    __CONFIRMATION_TEXT,
    case_sensitive=case_sensitive
  )
  assert (
    confirmation == expected_confirmation
  ), get_assertion_message("confirmation", expected_confirmation, confirmation)

@pytest.fixture(params=["YES"], autouse=True)
def __mock_input(request):
  with patch("builtins.input") as mock_method:
    mock_method.return_value = request.param
    yield mock_method
