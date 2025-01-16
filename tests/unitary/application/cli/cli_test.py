import os
import sys
from unittest.mock import patch, Mock

import pytest

from xmipp3_installer.application.cli import cli
from xmipp3_installer.application.cli import arguments
from xmipp3_installer.installer import installer_service

from .... import get_assertion_message

__USER = "test@test.com"
__DUMMY_PATH = "/path/to/dummy"
__DEFAULT_JOBS = 4
__DEFAULT_COMPILATION_ARGS = {
	"branch": None,
	"jobs": __DEFAULT_JOBS,
	"keep_output": False
}

def test_calls_add_default_usage_mode(
	__mock_sys_argv,
	__mock_add_default_usage_mode,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	cli.main()
	__mock_add_default_usage_mode.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["test"], ["test"]),
		pytest.param(["all"], ["all"]),
		pytest.param([], ["all"])
	],
	indirect=["__mock_sys_argv"]
)
def test_adds_default_usage_mode(__mock_sys_argv, expected_args):
	cli.__add_default_usage_mode()
	assert (
		sys.argv == [arguments.XMIPP_PROGRAM_NAME, *expected_args]
	), get_assertion_message("arguments", [arguments.XMIPP_PROGRAM_NAME, *expected_args], sys.argv)

def test_calls_parse_args(
	__mock_sys_argv,
	__mock_add_default_usage_mode,
	__mock_parse_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	cli.main()
	__mock_parse_args.assert_called_once_with()

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(
			["addModel", __USER, __DUMMY_PATH],
			{"login": __USER, "modelPath": __DUMMY_PATH}
		),
		pytest.param(
			["addModel", __USER, __DUMMY_PATH, "--update"],
			{"login": __USER, "modelPath": __DUMMY_PATH, "update": True}
		),
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_add_model(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("addModel", {"update": False}, expected_args, __mock_run_installer)

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
		pytest.param(["--keep-output"], {"keep_output": True}),
		pytest.param(
			["-j=20", "--keep-output", "-b", "test_branch"],
			{"jobs": 20, "keep_output": True, "branch": "test_branch"}
		)
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_all_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_get_default_job_number,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("all", __DEFAULT_COMPILATION_ARGS, expected_args, __mock_run_installer)

def test_returns_expected_mode_clean_all_args(
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	with patch.object(sys, 'argv', [arguments.XMIPP_PROGRAM_NAME, "cleanAll"]):
		__test_args_in_mode("cleanAll", {}, {}, __mock_run_installer)

def test_returns_expected_mode_clean_bin_args(
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	with patch.object(sys, 'argv', [arguments.XMIPP_PROGRAM_NAME, "cleanBin"]):
		__test_args_in_mode("cleanBin", {}, {}, __mock_run_installer)

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["compileAndInstall"], {}),
		pytest.param(["compileAndInstall", "-j", "8"], {"jobs": 8}),
		pytest.param(["compileAndInstall", "-j=8"], {"jobs": 8}),
		pytest.param(["compileAndInstall", "-b", "test"], {"branch": "test"}),
		pytest.param(["compileAndInstall", "-b=test"], {"branch": "test"}),
		pytest.param(["compileAndInstall", "--branch", "test2"], {"branch": "test2"}),
		pytest.param(["compileAndInstall", "--branch=test2"], {"branch": "test2"}),
		pytest.param(["compileAndInstall", "--keep-output"], {"keep_output": True}),
		pytest.param(
			["compileAndInstall", "-j=20", "--keep-output", "-b", "test_branch"],
			{"jobs": 20, "keep_output": True, "branch": "test_branch"}
		)
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_compile_and_install_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_get_default_job_number,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("compileAndInstall", __DEFAULT_COMPILATION_ARGS, expected_args, __mock_run_installer)

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["configBuild"], {}),
		pytest.param(["configBuild", "--keep-output"], {"keep_output": True})
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_config_build_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("configBuild", {"keep_output": False}, expected_args, __mock_run_installer)

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["config"], {}),
		pytest.param(["config", "-o"], {"overwrite": True}),
		pytest.param(["config", "--overwrite"], {"overwrite": True})
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_config_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("config", {"overwrite": False}, expected_args, __mock_run_installer)

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["getModels"], {}),
		pytest.param(["getModels", "-d", __DUMMY_PATH], {"directory": __DUMMY_PATH}),
		pytest.param(["getModels", "--directory", __DUMMY_PATH], {"directory": __DUMMY_PATH}),
		pytest.param(["getModels", f"-d={__DUMMY_PATH}"], {"directory": __DUMMY_PATH})
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_get_models_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_get_project_root_subpath,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("getModels", {"directory": os.path.join(__DUMMY_PATH, "default")}, expected_args, __mock_run_installer)

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["getSources"], {}),
		pytest.param(["getSources", "-b", "test_branch"], {"branch": "test_branch"}),
		pytest.param(["getSources", "--branch", "test_branch"], {"branch": "test_branch"}),
		pytest.param(["getSources", "-b=test_branch"], {"branch": "test_branch"}),
		pytest.param(["getSources", "--keep-output"], {"keep_output": True}),
		pytest.param(
			["getSources", "--branch=test_branch", "--keep-output"],
			{"branch": "test_branch", "keep_output": True}
		)
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_get_sources_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("getSources", {"branch": None, "keep_output": False}, expected_args, __mock_run_installer)

def test_returns_expected_mode_git_args(
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	with patch.object(sys, 'argv', [arguments.XMIPP_PROGRAM_NAME, "git", "clone", "test_url"]):
		__test_args_in_mode("git", {}, {"command": ["clone", "test_url"]}, __mock_run_installer)

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["test", "mytest"], {"testName": "mytest"}),
		pytest.param(["test", "mytest", "--show"], {"testName": "mytest", "show": True}),
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_test_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("test", {"show": False}, expected_args, __mock_run_installer)

@pytest.mark.parametrize(
	"__mock_sys_argv,expected_args",
	[
		pytest.param(["version"], {}),
		pytest.param(["version", "--short"], {"short": True}),
	],
	indirect=["__mock_sys_argv"]
)
def test_returns_expected_mode_version_args(
	expected_args,
	__mock_sys_argv,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	__test_args_in_mode("version", {"short": False}, expected_args, __mock_run_installer)

def test_calls_validate_args(
	__mock_sys_argv,
	__mock_add_default_usage_mode,
	__mock_parse_args,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer,
	__mock_sys_exit
):
	cli.main()
	__mock_validate_args.assert_called_once()

@pytest.mark.parametrize(
	"args,exit_with_error",
	[
		pytest.param({}, False),
		pytest.param({"jobs": 1}, False),
		pytest.param({"jobs": 0}, True),
		pytest.param({"jobs": -1}, True),
		pytest.param({"branch": None}, False),
		pytest.param({"branch": "mybranch"}, False),
		pytest.param({"branch": "my branch"}, True),
	],
)
def test_returns_expected_arg_validation(
	args,
	exit_with_error,
	__mock_stdout_stderr
):
	parser = cli.__generate_parser()
	if exit_with_error:
		with pytest.raises(SystemExit):
			cli.__validate_args(args, parser)
	else:
		cli.__validate_args(args, parser)

def test_deactivates_output_substitution_on_args_validation(
	__mock_logger_set_allow_substitution
):
	cli.__validate_args({"keep_output": True}, cli.__generate_parser())
	__mock_logger_set_allow_substitution.assert_called_once_with(False)

@pytest.mark.parametrize(
	"args",
	[
		pytest.param({}),
		pytest.param({"keep_output": False})
	],
)
def test_does_not_deactivate_output_substitution_on_args_validation(
	args,
	__mock_logger_set_allow_substitution
):
	cli.__validate_args(args, cli.__generate_parser())
	__mock_logger_set_allow_substitution.assert_not_called()

@pytest.mark.parametrize(
	"__mock_run_installer",
	[
		pytest.param(0),
		pytest.param(1),
		pytest.param(20)
	],
	indirect=["__mock_run_installer"]
)
def test_exits_with_expected_ret_code_on_main(
	__mock_sys_argv,
	__mock_add_default_usage_mode,
	__mock_parse_args,
	__mock_validate_args,
	__mock_stdout_stderr,
	__mock_run_installer
):
	expected_ret_code = __mock_run_installer().run_installer()
	with pytest.raises(SystemExit) as pytest_exit:
		cli.main()
	assert (
		pytest_exit.value.code == expected_ret_code
	), get_assertion_message("exit code", expected_ret_code, pytest_exit.value.code)

def __test_args_in_mode(
	mode,
	default_args,
	expected_args,
	__mock_run_installer
):
	expected_args = {**default_args, "mode": mode, **expected_args}
	cli.main()
	__mock_run_installer.assert_called_once_with(expected_args)

@pytest.fixture(params=[["-h"]])
def __mock_sys_argv(request):
	with patch.object(sys, 'argv', [arguments.XMIPP_PROGRAM_NAME, *request.param]) as mock_object:
		yield mock_object

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
def __mock_get_default_job_number():
	with patch(
		"xmipp3_installer.application.cli.cli.__get_default_job_number"
	) as mock_method:
		mock_method.return_value = __DEFAULT_JOBS
		yield mock_method

@pytest.fixture
def __mock_stdout_stderr():
	with patch('sys.stdout', new_callable=lambda: open(os.devnull, 'w')), \
	patch('sys.stderr', new_callable=lambda: open(os.devnull, 'w')):
		yield

@pytest.fixture
def __mock_get_project_root_subpath():
	with patch(
		"xmipp3_installer.application.cli.cli.__get_project_root_subpath"
	) as mock_method:
		mock_method.return_value = os.path.join(__DUMMY_PATH, "default")
		yield mock_method

@pytest.fixture
def __mock_logger_set_allow_substitution():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.set_allow_substitution"
	) as mock_method:
		yield mock_method

@pytest.fixture(params=[0])
def __mock_run_installer(request):
	mock_installation_manager = Mock()
	mock_installation_manager.run_installer.return_value = request.param
	with patch(
		"xmipp3_installer.installer.installer_service.InstallationManager"
	) as mock_class:
		mock_class.return_value = mock_installation_manager
		yield mock_class

@pytest.fixture
def __mock_sys_exit():
	with patch("sys.exit") as mock_method:
		yield mock_method
