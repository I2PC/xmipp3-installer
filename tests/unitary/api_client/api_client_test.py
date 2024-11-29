import http.client
import json
import ssl
from unittest.mock import patch

import pytest

from xmipp3_installer.api_client import api_client
from xmipp3_installer.installer import urls

__CONTEXT = ssl._create_unverified_context()

def test_does_not_call_httpsconnection_when_sending_empty_installation_attempt(
  __mock_httpsconnection,
  __mock_create_unverified_context
):
  api_client.send_installation_attempt(None)
  __mock_httpsconnection.assert_not_called()

def test_calls_httpsconnection_when_sending_installation_attempt(
  __mock_httpsconnection,
  __mock_create_unverified_context
):
  api_client.send_installation_attempt({})
  __mock_httpsconnection.assert_called_once_with(
    urls.API_URL[:urls.API_URL.index("/")],
    context=__CONTEXT
  )

def test_calls_connection_request_when_sending_installation_attempt(
  __mock_httpsconnection
):
  installation_info = {"var1": "value1", "var2": "value2"}
  api_client.send_installation_attempt(installation_info)
  __mock_httpsconnection().request.assert_called_once_with(
    "POST",
    urls.API_URL[urls.API_URL.index("/"):],
    json.dumps(installation_info),
    {"Content-type": "application/json"}
  )

def test_calls_connection_close_when_sending_installation_attempt(
  __mock_httpsconnection
):
  api_client.send_installation_attempt({})
  __mock_httpsconnection().close.assert_called_once_with()

@pytest.fixture
def __mock_httpsconnection():
  with patch.object(http.client, "HTTPSConnection") as mock_object:
    yield mock_object

@pytest.fixture
def __mock_create_unverified_context():
  with patch("ssl._create_unverified_context") as mock_method:
    mock_method.return_value = __CONTEXT
    yield mock_method
