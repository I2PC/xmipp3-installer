import http.client
import json
import ssl
from unittest.mock import patch

import pytest

from xmipp3_installer.api_client import api_client
from xmipp3_installer.installer import urls

def test_does_not_call_httpsconnection_when_sending_empty_installation_attempt(
  __mock_httpconnection
):
  api_client.send_installation_attempt(None)
  __mock_httpconnection.assert_not_called()

def test_calls_httpsconnection_when_sending_installation_attempt(
  __mock_httpconnection
):
  api_client.send_installation_attempt({})
  __mock_httpconnection.assert_called_once_with(
    urls.API_URL[:urls.API_URL.index("/")]
  )

def test_calls_connection_request_when_sending_installation_attempt(
  __mock_httpconnection
):
  installation_info = {"var1": "value1", "var2": "value2"}
  api_client.send_installation_attempt(installation_info)
  __mock_httpconnection().request.assert_called_once_with(
    "POST",
    urls.API_URL[urls.API_URL.index("/"):],
    body=json.dumps(installation_info),
    headers={"Content-type": "application/json"}
  )

def test_calls_connection_close_when_sending_installation_attempt(
  __mock_httpconnection
):
  api_client.send_installation_attempt({})
  __mock_httpconnection().close.assert_called_once_with()

@pytest.fixture
def __mock_httpconnection():
  with patch.object(http.client, "HTTPConnection") as mock_object:
    yield mock_object
