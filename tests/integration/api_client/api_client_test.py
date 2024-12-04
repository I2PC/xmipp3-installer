import http.client
import os
import shlex
import ssl
import tempfile
from unittest.mock import patch

import pytest

from xmipp3_installer.installer import constants, urls
from xmipp3_installer.api_client import api_client
from xmipp3_installer.api_client.assembler import installation_info_assembler

from . import shell_command_outputs, file_contents
from ... import get_assertion_message

def test_calls_api_when_sending_installation_attempt(
	__mock_mac_address,
	__mock_library_versions_file,
	__mock_run_parallel_jobs,
	__mock_get_release_name,
	__mock_get_architecture_name,
	__mock_get_current_branch,
	__mock_is_branch_up_to_date,
	__mock_log_tail,
	__mock_server
):
	api_client.send_installation_attempt(
		installation_info_assembler.get_installation_info()
	)
	n_requests = len(__mock_server.requests)
	assert (n_requests == 1), get_assertion_message("number of API calls", 1, n_requests)
	assert (
		__mock_server.requests[0].method == "POST"
	), get_assertion_message("request method", "POST", __mock_server.requests[0].method)

@pytest.fixture
def __mock_mac_address(fake_process):
	fake_process.register_subprocess(
		shlex.split("ip addr"),
		stdout=shell_command_outputs.IP_ADDR
	)
	yield fake_process

@pytest.fixture
def __mock_file():
	with tempfile.NamedTemporaryFile(
		delete=False,
		dir=os.path.dirname(os.path.abspath(__file__))
	) as temp_file:
		try:
			yield temp_file
		finally:
			temp_file.close()
			os.remove(temp_file.name)

@pytest.fixture
def __mock_library_versions_file(__mock_file):
	with patch.object(constants, "LIBRARY_VERSIONS_FILE", __mock_file.name):
		with open(__mock_file.name, "w") as versions_file:
			versions_file.write(file_contents.CMAKE_LIB_VERSIONS)
		yield

@pytest.fixture
def __mock_get_release_name(fake_process):
	fake_process.register_subprocess(
		shlex.split("cat /etc/os-release"),
		stdout=shell_command_outputs.OS_RELEASE
	)
	yield fake_process

@pytest.fixture
def __mock_get_architecture_name(fake_process):
	fake_process.register_subprocess(
		shlex.split("cat /sys/devices/cpu/caps/pmu_name"),
		stdout=shell_command_outputs.PMU_NAME
	)
	yield fake_process

@pytest.fixture(params=[True])
def __mock_get_current_branch(fake_process, request):
	is_master = request.param
	branch = shell_command_outputs.get_current_branch(is_master)
	fake_process.register_subprocess(
		shlex.split("git rev-parse --abbrev-ref HEAD"),
		stdout=branch,
		occurrences=2
	)
	yield fake_process

@pytest.fixture(params=[(True, shell_command_outputs.MASTER_BRANCH)])
def __mock_is_branch_up_to_date(fake_process, request):
	up_to_date, branch = request.param
	local_commit, remote_commit = shell_command_outputs.get_latest_commits(up_to_date)
	fake_process.register_subprocess(shlex.split("git fetch"))
	fake_process.register_subprocess(
		shlex.split(f"git rev-parse {branch}"),
		stdout=local_commit
	)
	fake_process.register_subprocess(
		shlex.split(f"git rev-parse origin/{branch}"),
		stdout=remote_commit
	)
	yield fake_process

@pytest.fixture(params=[True])
def __mock_log_tail(fake_process, request):
	log_file_content = file_contents.LOG_TAIL_SUCCES if request.param else file_contents.LOG_TAIL_ERROR
	fake_process.register_subprocess(
		shlex.split(f"tail -n {constants.TAIL_LOG_NCHARS} {constants.LOG_FILE}"),
		stdout=log_file_content
	)
	yield fake_process

@pytest.fixture
def __mock_run_parallel_jobs():
	def __mimick_run_parallel_jobs(funcs, func_args, _=1):
		results = []
		for func, args in zip(funcs, func_args):
			results.append(func(*args))
		return results
	with patch("xmipp3_installer.installer.orquestrator.run_parallel_jobs") as mock_method:
		mock_method.side_effect = __mimick_run_parallel_jobs
		yield mock_method

@pytest.fixture
def __mock_server(httpsserver, __add_ssl_context):
	httpsserver.serve_content(content=None, code=200, store_request_data=True)
	with patch.object(urls, "API_URL", f"{httpsserver.url}/attempts"):
		yield httpsserver

@pytest.fixture
def __add_ssl_context():
	def add_ssl_param(parsed_url, timeout_seconds):
		return http.client.HTTPSConnection(
			parsed_url.hostname,
			parsed_url.port,
			timeout=timeout_seconds,
			context=ssl._create_unverified_context()
		)
	with patch(
		"xmipp3_installer.api_client.api_client.__get_https_connection"
	) as mock_connection:
		mock_connection.side_effect = add_ssl_param
		yield mock_connection
