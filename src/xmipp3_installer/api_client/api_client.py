"""### Contains an API client that registers the installation attempts."""

import http.client
import json
from typing import Dict
from urllib.parse import urlparse

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
		conn = http.client.HTTPConnection(parsed_url.hostname, parsed_url.port)
		conn.request("POST", parsed_url.path, body=params, headers=headers)
		conn.close()
