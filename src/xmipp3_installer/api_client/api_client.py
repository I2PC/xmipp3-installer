"""### Contains an API client that registers the installation attempts."""

import http.client
import json
from typing import Dict
from urllib.parse import urlparse, ParseResult

from xmipp3_installer.installer import urls

def send_installation_attempt(installation_info: Dict):
	"""
	### Sends a POST request to Xmipp's metrics's API.
	
	#### Params:
	- installation_info (dict): Dictionary containing all the installation information.
	"""
	if installation_info is not None:
		params = json.dumps(installation_info)
		headers = {"Content-type": "application/json"}
		parsed_url = urlparse(urls.API_URL)
		conn = __get_https_connection(parsed_url)
		conn.request("POST", parsed_url.path, body=params, headers=headers)
		conn.close()

def __get_https_connection(parsed_url: ParseResult) -> http.client.HTTPSConnection:
	"""
	### Establishes the connection needed to send the API call.
	Separated to enable integration & E2E tests.

	#### Params:
	- parsed_url (ParseResult): Object containing all elements of the url.

	#### Returns:
	- (HTTPSConnection): Established connection.
	"""
	return http.client.HTTPSConnection(parsed_url.hostname, parsed_url.port)
