import sys
from unittest.mock import patch

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments

__DEFAULT_JOBS = 4
__DEFAULT_ARGS = {
	"branch": None,
	"jobs": __DEFAULT_JOBS,
	"keep_output": False
}

def test_calls_add_default_usage_mode(
	__mock_sys_argv, 
	__mock_add_default_usage_mode,
	__mock_print
):
	cli.main()
	__mock_add_default_usage_mode.assert_called_once()

def test_calls_parse_args(
	__mock_sys_argv,
	__mock_add_default_usage_mode,
	__mock_parse_args,
	__mock_print
):
	cli.main()
	__mock_parse_args.assert_called_once()

def test_calls_validate_args(
	__mock_sys_argv,
	__mock_add_default_usage_mode,
	__mock_parse_args,
	__mock_validate_args,
	__mock_move_to_root_dir,
	__mock_print
):
	cli.main()
	__mock_validate_args.assert_called_once()

def test_calls_move_to_root_dir(
	__mock_sys_argv,
	__mock_add_default_usage_mode,
	__mock_parse_args,
	__mock_validate_args,
	__mock_move_to_root_dir,
	__mock_print
):
	cli.main()
	__mock_move_to_root_dir.assert_called_once()

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param([], {}),
		pytest.param(["all"], {}),
		pytest.param(["-j", "8"], {"jobs": 8}),
		pytest.param(["-j=8"], {"jobs": 8}),
		pytest.param(["-b", "test"], {"branch": "test"}),
		pytest.param(["-b=test"], {"branch": "test"}),
		pytest.param(["--branch", "test2"], {"branch": "test2"}),
		pytest.param(["--branch=test2"], {"branch": "test2"}),
		pytest.param(["--keep-output"], {"keep_output": True})
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_all_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_move_to_root_dir,
	__mock_get_default_job_number,
	__mock_print
):
	expected_args = {**__DEFAULT_ARGS, "mode": "all", **expected_args}
	assert (cli.main() == expected_args), "Generated different args than expected for mode \"all\"."

@pytest.fixture
def __mock_sys_argv(request):
	args = request.param if hasattr(request, "param") else ["-h"]
	with patch.object(sys, 'argv', [arguments.XMIPP_PROGRAM_NAME, *args]):
		yield

@pytest.fixture
def __mock_add_default_usage_mode():
	with patch(
		"xmipp3_installer.application.cli.cli.__add_default_usage_mode"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_parse_args():
	with patch(
		"argparse.ArgumentParser.parse_args"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_validate_args():
	with patch(
		"xmipp3_installer.application.cli.cli.__validate_args"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_move_to_root_dir():
	with patch(
		"xmipp3_installer.application.cli.cli.__move_to_root_dir"
	) as mock_method:
		yield mock_method

@pytest.fixture
def __mock_get_default_job_number():
	with patch(
		"xmipp3_installer.application.cli.cli.__get_default_job_number"
	) as mock_method:
		mock_method.return_value = __DEFAULT_JOBS
		yield mock_method

@pytest.fixture
def __mock_print():
	with patch("builtins.print") as mock_method:
		yield mock_method
