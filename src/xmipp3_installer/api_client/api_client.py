"""### Contains an API client that registers the installation attempts."""

import http.client
import json
from typing import Dict
from urllib.parse import urlparse, ParseResult

from xmipp3_installer.installer import urls
from xmipp3_installer.application.logger.logger import logger

def send_installation_attempt(installation_info: Dict):
  """
  ### Sends a POST request to Xmipp's metrics's API.
  
  #### Params:
  - installation_info (dict): Dictionary containing all the installation information.
  """
  if installation_info is None:
    return
  params = json.dumps(installation_info)
  headers = {"Content-type": "application/json"}
  parsed_url = urlparse(urls.API_URL)
  conn = None
  try:
    conn = __get_https_connection(parsed_url, 6)
    conn.request("POST", parsed_url.path, body=params, headers=headers)
    conn.getresponse()
  except TimeoutError:
    logger(
      logger.yellow("There was a timeout while sending installation data."),
      show_in_terminal=False
    )
  finally:
    if conn is not None:
      conn.close()


def __get_https_connection(parsed_url: ParseResult, timeout_seconds: int) -> http.client.HTTPSConnection:
  """
  ### Establishes the connection needed to send the API call.
  
  Separated to enable integration & E2E tests.

  #### Params:
  - parsed_url (ParseResult): Object containing all elements of the url.
  - timeout_seconds (int): Number of seconds to wait until a timeout.

  #### Returns:
  - (HTTPSConnection): Established connection.
  """
  return http.client.HTTPSConnection(parsed_url.hostname or "localhost", parsed_url.port, timeout=timeout_seconds)
