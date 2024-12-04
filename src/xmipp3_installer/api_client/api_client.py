"""### Contains an API client that registers the installation attempts."""

import http.client
import json
import ssl
from typing import Dict

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

		url = urls.API_URL.split("/", maxsplit=1)
		path = f"/{url[1]}"
		url = url[0]
		conn = http.client.HTTPSConnection(
			url,
			context=ssl._create_unverified_context() # Unverified context because url does not have an ssl certificate
		)
		conn.request("POST", path, body=params, headers=headers)
		conn.close()
