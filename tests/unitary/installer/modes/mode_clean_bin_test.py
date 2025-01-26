from unittest.mock import patch, MagicMock, call

import pytest

from xmipp3_installer.application.logger import errors
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.modes.mode_clean_bin_executor import ModeCleanBinExecutor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.tmp import versions

from .... import get_assertion_message

def test_implements_interface_mode_executor():
	executor = ModeCleanBinExecutor({})
	assert (
		isinstance(executor, ModeExecutor)
	), get_assertion_message(
		"parent class",
		ModeExecutor.__name__,
		executor.__class__.__bases__[0].__name__
	)

def test_does_not_override_parent_config_values(__dummy_test_mode_executor):
	base_executor = __dummy_test_mode_executor({})
	base_executor.run()  # To cover dummy implementation execution
	config_executor = ModeCleanBinExecutor({})
	base_config = (
		base_executor.logs_to_file,
		base_executor.prints_with_substitution,
		base_executor.prints_banner_on_exit
	)
	inherited_config = (
		config_executor.logs_to_file,
		config_executor.prints_with_substitution,
		config_executor.prints_banner_on_exit
	)
	assert (
		inherited_config == base_config
	), get_assertion_message("config values", base_config, inherited_config)

def test_calls_logger_when_getting_confirmation(
	__mock_logger,
	__mock_logger_yellow,
	__mock_get_user_confirmation
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_confirmation()
	expected_message = __mock_logger_yellow(
		f"WARNING: This will DELETE from {constants.SOURCES_PATH} all *.so, *.os and *.o files. Also the *.pyc and *.dblite files"
	)
	expected_message += f"\n{__mock_logger_yellow(
		'If you are sure you want to do this, type \'y\' (case sensitive):'
	)}"
	__mock_logger.assert_called_once_with(expected_message)

def test_calls_get_user_confirmation_when_getting_confirmation(
	__mock_get_user_confirmation
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_confirmation()
	__mock_get_user_confirmation.assert_called_once_with("y")

@pytest.mark.parametrize(
	"__mock_get_user_confirmation",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_get_user_confirmation"]
)
def test_gets_expected_user_confirmation(
	__mock_get_user_confirmation
):
	confirmation = ModeCleanBinExecutor._ModeCleanBinExecutor__get_confirmation()
	assert (
		confirmation == __mock_get_user_confirmation()
	), get_assertion_message(
		"user confirmation",
		__mock_get_user_confirmation(),
		confirmation
	)

def test_calls_path_rglob_when_getting_pycache_dirs(
	__mock_path
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_pycache_dirs()
	__mock_path().rglob.assert_called_once_with("__pycache__")
	
@pytest.mark.parametrize(
	"expected_dirs",
	[
		pytest.param([]),
		pytest.param(["/path/to/file1"]),
		pytest.param(["/path/to/file1", "/path/to/file2"])
	]
)
def test_returns_expected_pycache_dirs(__mock_path, expected_dirs):
	__mock_path().rglob.return_value = expected_dirs
	pycache_dirs = ModeCleanBinExecutor._ModeCleanBinExecutor__get_pycache_dirs()
	assert (
		pycache_dirs == expected_dirs
	), get_assertion_message("pycache dirs", expected_dirs, pycache_dirs)

def test_calls_os_walk_when_getting_empty_dirs(
	__mock_os_walk,
	__mock_os_path_join
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_empty_dirs()
	__mock_os_walk.assert_called_once_with(
		__mock_os_path_join(
			constants.SOURCES_PATH,
			versions.XMIPP,
			"applications",
			"programs"
		)
	)

def test_returns_expected_empty_dirs(__mock_os_walk):
	__mock_os_walk.return_value = [
		("dist", ["folder1", "folder2"], []),
		("dist/folder1", [], ["file1"]),
		("dist/folder2", ["subfolder1", "subfolder2"], []),
		("dist/folder2/subfolder1", [], []),
		("dist/folder2/subfolder2", ["empty"], []),
		("dist/folder2/subfolder2/empty", [], [])
	]
	expected_empty_dirs = [
		"dist/folder2/subfolder1",
		"dist/folder2/subfolder2/empty"
	]
	empty_dirs = ModeCleanBinExecutor._ModeCleanBinExecutor__get_empty_dirs()
	assert (
		empty_dirs == expected_empty_dirs
	), get_assertion_message("empty directories", expected_empty_dirs, empty_dirs)

def test_calls_glob_when_getting_compilation_files(__mock_glob):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_compilation_files()
	__mock_glob.assert_has_calls([
		call('**/*.so', recursive=True, root_dir=constants.SOURCES_PATH),
		call('**/*.os', recursive=True, root_dir=constants.SOURCES_PATH),
		call('**/*.o', recursive=True, root_dir=constants.SOURCES_PATH)
	])
	assert (
		__mock_glob.call_count == 3
	), get_assertion_message("call count", 3, __mock_glob.call_count)

def test_returns_expected_compilation_files(__mock_glob):
	__mock_glob.side_effect = [["file1"], ["file2", "file3"], ["file4"]]
	expected_compilation_files = ["file1", "file2", "file3", "file4"]
	compilation_files = ModeCleanBinExecutor._ModeCleanBinExecutor__get_compilation_files()
	assert (
		compilation_files == expected_compilation_files
	), get_assertion_message("compilation files", expected_compilation_files, compilation_files)

def test_calls_glob_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_paths_to_delete()
	__mock_glob.assert_called_once_with("**/.dblite", recursive=True)

def test_calls_get_compilation_files_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_paths_to_delete()
	__mock_get_compilation_files.assert_called_once_with()

def test_calls_get_empty_dirs_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_paths_to_delete()
	__mock_get_empty_dirs.assert_called_once_with()

def test_calls_get_pycache_dirs_when_getting_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	ModeCleanBinExecutor._ModeCleanBinExecutor__get_paths_to_delete()
	__mock_get_pycache_dirs.assert_called_once_with()

def test_returns_expected_paths_to_delete(
	__mock_glob,
	__mock_get_compilation_files,
	__mock_get_empty_dirs,
	__mock_get_pycache_dirs
):
	__mock_glob.return_value = ["globfile"]
	expected_paths_to_delete = [
		*__mock_glob(),
		*__mock_get_compilation_files(),
		*__mock_get_empty_dirs(),
		*__mock_get_pycache_dirs(),
		constants.BUILD_PATH
	]
	paths_to_delete = ModeCleanBinExecutor._ModeCleanBinExecutor__get_paths_to_delete()
	assert (
		paths_to_delete == expected_paths_to_delete
	), get_assertion_message("paths to delete", expected_paths_to_delete, paths_to_delete)

def test_calls_get_confirmation_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_logger
):
	ModeCleanBinExecutor({}).run()
	__mock_get_confirmation.assert_called_once_with()

def test_calls_get_paths_to_delete_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_logger
):
	ModeCleanBinExecutor({}).run()
	__mock_get_paths_to_delete.assert_called_once_with()

def test_calls_delete_paths_to_delete_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_delete_paths,
	__mock_logger
):
	ModeCleanBinExecutor({}).run()
	__mock_delete_paths.assert_called_once_with([
		*__mock_get_paths_to_delete(),
		constants.BUILD_PATH
	])

def test_calls_logger_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_delete_paths,
	__mock_logger,
	__mock_get_done_message
):
	ModeCleanBinExecutor({}).run()
	__mock_logger.assert_called_once_with(
		__mock_get_done_message()
	)

@pytest.mark.parametrize(
	"__mock_get_confirmation",
	[pytest.param(False), pytest.param(True)],
	indirect=["__mock_get_confirmation"]
)
def test_returns_expected_values_when_running_executor(
	__mock_get_confirmation,
	__mock_get_paths_to_delete,
	__mock_delete_paths,
	__mock_logger,
	__mock_get_done_message
):
	expected_values = (0, "") if __mock_get_confirmation() else (errors.INTERRUPTED_ERROR, "")
	values = ModeCleanBinExecutor({}).run()
	assert (
		values == expected_values
	), get_assertion_message("return values", expected_values, values)

@pytest.fixture
def __dummy_test_mode_executor():
	class TestExecutor(ModeExecutor):
		def run(self):
			return (0, "")
	return TestExecutor

@pytest.fixture(autouse=True)
def __mock_logger():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.__call__"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_logger_yellow():
	with patch(
		"xmipp3_installer.application.logger.logger.Logger.yellow"
	) as mock_method:
		mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
		yield mock_method

@pytest.fixture(autouse=True, params=[True])
def __mock_get_user_confirmation(request):
	with patch(
		"xmipp3_installer.application.user_interactions.get_user_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_path():
	new_path = MagicMock()
	new_path.rglob.return_value = ['/path/to/file1', '/path/to/file2']
	with patch("pathlib.Path") as mock_object:
		mock_object.return_value = new_path
		yield mock_object

@pytest.fixture(autouse=True)
def __mock_os_walk():
	with patch("os.walk") as mock_method:
		mock_method.return_value = [("", [], [])]
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_os_path_join():
	with patch("os.path.join") as mock_method:
		mock_method.side_effect = lambda *args: '/'.join([*args])
		yield mock_method

@pytest.fixture
def __mock_glob():
	with patch("glob.glob") as mock_method:
		mock_method.return_value = []
		yield mock_method

@pytest.fixture
def __mock_get_compilation_files():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_compilation_files"
	) as mock_method:
		mock_method.return_value = ["compilation_file1", "compilation_file2"]
		yield mock_method

@pytest.fixture
def __mock_get_empty_dirs():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_empty_dirs"
	) as mock_method:
		mock_method.return_value = ["empty_dir"]
		yield mock_method

@pytest.fixture
def __mock_get_pycache_dirs():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_pycache_dirs"
	) as mock_method:
		mock_method.return_value = ["__pycache__"]
		yield mock_method

@pytest.fixture(params=[True])
def __mock_get_confirmation(request):
	with patch(
		"xmipp3_installer.installer.modes.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_confirmation"
	) as mock_method:
		mock_method.return_value = request.param
		yield mock_method

@pytest.fixture
def __mock_get_paths_to_delete():
	with patch(
		"xmipp3_installer.installer.modes.mode_clean_bin_executor.ModeCleanBinExecutor._ModeCleanBinExecutor__get_paths_to_delete"
	) as mock_method:
		mock_method.return_value = ["path1", "path2"]
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_delete_paths():
	with patch(
		"xmipp3_installer.repository.file_operations.delete_paths"
	) as mock_method:
		yield mock_method

@pytest.fixture(autouse=True)
def __mock_get_done_message():
	with patch(
		"xmipp3_installer.application.logger.predefined_messages.get_done_message"
	) as mock_method:
		mock_method.return_value = "Done message"
		yield mock_method
