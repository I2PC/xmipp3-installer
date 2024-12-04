import http.client
import json
from unittest.mock import patch
from urllib.parse import urlparse

import pytest

from xmipp3_installer.api_client import api_client
from xmipp3_installer.installer import urls

__API_URL = "https://hostname/path"
__PARSED_URL = urlparse(__API_URL)

def test_does_not_call_httpsconnection_when_sending_empty_installation_attempt(
  __mock_httpsconnection
):
  api_client.send_installation_attempt(None)
  __mock_httpsconnection.assert_not_called()

def test_calls_httpsconnection_when_sending_installation_attempt(
  __mock_httpsconnection
):
  api_client.send_installation_attempt({})
  __mock_httpsconnection.assert_called_once_with(
    __PARSED_URL.hostname,
    __PARSED_URL.port
  )

def test_calls_connection_request_when_sending_installation_attempt(
  __mock_httpsconnection
):
  installation_info = {"var1": "value1", "var2": "value2"}
  api_client.send_installation_attempt(installation_info)
  __mock_httpsconnection().request.assert_called_once_with(
    "POST",
    __PARSED_URL.path,
    body=json.dumps(installation_info),
    headers={"Content-type": "application/json"}
  )

def test_calls_connection_close_when_sending_installation_attempt(
  __mock_httpsconnection
):
  api_client.send_installation_attempt({})
  __mock_httpsconnection().close.assert_called_once_with()

@pytest.fixture
def __mock_httpsconnection(__mock_api_url):
  with patch.object(http.client, "HTTPSConnection") as mock_object:
    yield mock_object

@pytest.fixture
def __mock_api_url():
  with patch.object(urls, "API_URL", __API_URL):
    yield
