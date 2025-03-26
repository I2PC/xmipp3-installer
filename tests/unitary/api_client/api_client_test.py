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
    __PARSED_URL.port,
    timeout=6
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

def test_calls_connection_getresponse_when_sending_installation_attempt(
  __mock_httpsconnection
):
  api_client.send_installation_attempt({})
  __mock_httpsconnection().getresponse.assert_called_once_with()

def test_calls_logger_when_sending_installation_attempt_and_receives_timeout(
  __mock_httpsconnection,
  __mock_timeout,
  __mock_logger,
  __mock_logger_yellow
):
  api_client.send_installation_attempt({})
  __mock_logger.assert_called_once_with(
     __mock_logger_yellow("There was a timeout while sending installation data."),
     show_in_terminal=False
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

@pytest.fixture
def __mock_timeout():
  with patch("http.client.HTTPSConnection") as mock_method:
    mock_method.side_effect = TimeoutError()
    yield mock_method

@pytest.fixture
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"format-start-{text}-format-end"
		yield mock_method
