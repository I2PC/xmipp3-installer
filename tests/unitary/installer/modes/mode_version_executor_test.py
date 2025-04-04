from unittest.mock import patch, call

import pytest

from xmipp3_installer.application.cli.arguments import params
from xmipp3_installer.application.logger.logger import logger
from xmipp3_installer.installer import constants
from xmipp3_installer.installer.constants import paths
from xmipp3_installer.installer.modes import mode_version_executor
from xmipp3_installer.installer.modes.mode_executor import ModeExecutor
from xmipp3_installer.installer.modes.mode_version_executor import ModeVersionExecutor
from xmipp3_installer.repository.config_vars import variables

from ... import DummyVersionsManager
from .... import (
  get_assertion_message, JSON_XMIPP_RELEASE_DATE,
  JSON_XMIPP_VERSION_NAME, JSON_XMIPP_VERSION_NUMBER
)

__CONTEXT = {
  params.PARAM_SHORT: False,
  constants.VERSIONS_CONTEXT_KEY: DummyVersionsManager()
}
__LEFT_TEXT_LEN = 5
__DATE = "dd/mm/yyyy"
__FIXED_DATES_SECTION_PART = f"""Release date: {JSON_XMIPP_RELEASE_DATE}
Compilation date: """
__SOURCE = constants.XMIPP_CORE
__COMMIT = "5c3a24f"
__SOURCE_LEFT_TEXT = f"{__SOURCE} branch: "
__TAG_NAME = "tags/v3.24.06-Oceanus"
__BRANCH_NAME = "devel"
__RELEASE_NAME = "Ubuntu 24.04"
__LIBRARIES_WITH_VERSIONS = {
  "CMake": '3.31.3',
  "CC": 'GNU-13.3.0',
  'CXX': 'GNU-13-3-0',
  'Python3': '3.12.8',
  'MPI': '3.1',
  'HDF5': '1.10.10',
  'JPEG': '80',
  'SQLite3': '3.45.1',
  'Java': '17.0.13'
}
__LIBRARIES_WITH_VERSION_SECTION = '\n'.join([
  f"{library}: {version}"
  for library, version in __LIBRARIES_WITH_VERSIONS.items()
])
__SOURCE_PATH = paths.get_source_path(constants.XMIPP_CORE)

def test_implements_interface_mode_executor():
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  assert (
    isinstance(version_executor, ModeExecutor)
  ), get_assertion_message(
    "parent class",
    ModeExecutor.__name__,
    version_executor.__class__.__bases__[0].__name__
  )

def test_raises_key_error_when_short_param_not_provided():
  with pytest.raises(KeyError):
    ModeVersionExecutor({})

@pytest.mark.parametrize(
  "expected_short",
  [
    pytest.param(False),
    pytest.param(True),
    pytest.param(None)
  ]
)
def test_sets_short_value_to_introduced_value_in_args(expected_short):
  version_executor = ModeVersionExecutor({**__CONTEXT.copy(), params.PARAM_SHORT: expected_short})
  assert (
    version_executor.short == expected_short
  ), get_assertion_message("short value", expected_short, version_executor.short)

@pytest.mark.parametrize(
  "__mock_exists_init",
  [
    pytest.param([False, False]),
    pytest.param([False, True]),
    pytest.param([True, False]),
    pytest.param([True, True])
  ],
  indirect=["__mock_exists_init"]
)
def test_sets_library_file_exists_value_as_expected_when_initializing(__mock_exists_init):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  assert (
    version_executor.version_file_exists == __mock_exists_init(paths.LIBRARY_VERSIONS_FILE)
  ), get_assertion_message(
    "file exists values",
    __mock_exists_init(paths.LIBRARY_VERSIONS_FILE),
    version_executor.version_file_exists
  )

@pytest.mark.parametrize(
  "__mock_exists_init,expected_is_configured",
  [
    pytest.param([False, False], False),
    pytest.param([False, True], False),
    pytest.param([True, False], False),
    pytest.param([True, True], True)
  ],
  indirect=["__mock_exists_init"]
)
def test_sets_is_configured_values_as_expected_when_initializing(__mock_exists_init, expected_is_configured):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  assert (
    version_executor.is_configured == expected_is_configured
  ), get_assertion_message("is configured values", expected_is_configured, version_executor.is_configured)

def test_sets_version_values_as_expected_when_initializing():
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  values = (
    version_executor.xmipp_version_name,
    version_executor.xmipp_version_number,
    version_executor.release_date
  )
  expected_values = (
    JSON_XMIPP_VERSION_NAME,
    JSON_XMIPP_VERSION_NUMBER,
    JSON_XMIPP_RELEASE_DATE
  )
  assert (
    values == expected_values
  ), get_assertion_message("stored version values", expected_values, values)

def test_does_not_override_parent_config_values(__dummy_test_mode_executor):
  base_executor = __dummy_test_mode_executor(__CONTEXT.copy())
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  base_config = (
    base_executor.logs_to_file,
    base_executor.prints_with_substitution,
    base_executor.prints_banner_on_exit,
    base_executor.sends_installation_info
  )
  inherited_config = (
    version_executor.logs_to_file,
    version_executor.prints_with_substitution,
    version_executor.prints_banner_on_exit,
    version_executor.sends_installation_info
  )
  assert (
    inherited_config == base_config
  ), get_assertion_message("config values", base_config, inherited_config)

@pytest.mark.parametrize(
  "input_text,expected_result",
  [
    pytest.param("", "     "),
    pytest.param("a", "a    "),
    pytest.param("abcde", "abcde"),
    pytest.param("abcdef", "abcdef")
  ]
)
def test_returns_expected_text_when_adding_padding_spaces(
  input_text,
  expected_result,
  __mock_left_text_len
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  result_text = version_executor._ModeVersionExecutor__add_padding_spaces(input_text)
  assert (
    result_text == expected_result
  ), get_assertion_message("padded text", expected_result, result_text)

def test_calls_add_padding_spaces_when_getting_dates_section(
  __mock_add_padding_spaces
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_dates_section()
  __mock_add_padding_spaces.assert_has_calls([
    call('Release date: '),
    call('Compilation date: ')
  ])

@pytest.mark.parametrize(
  "config_file_exists,expected_compilation_date",
  [
    pytest.param(False, "-"),
    pytest.param(True, __DATE)
  ]
)
def test_returns_expected_dates_section(
  config_file_exists,
  expected_compilation_date,
  __mock_add_padding_spaces
):
  context = {
    **__CONTEXT.copy(),
    variables.LAST_MODIFIED_KEY: __DATE if config_file_exists else ''
  }
  version_executor = ModeVersionExecutor(context)
  dates_section = version_executor._ModeVersionExecutor__get_dates_section()
  expected_dates_section = f"{__FIXED_DATES_SECTION_PART}{expected_compilation_date}"
  assert (
    dates_section == expected_dates_section
  ), get_assertion_message("dates section", expected_dates_section, dates_section)

def test_calls_add_padding_spaces_when_getting_source_info(
  __mock_add_padding_spaces,
  __mock_exists
):
  __mock_exists.return_value = False
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
  __mock_add_padding_spaces.assert_called_once_with(__SOURCE_LEFT_TEXT)

def test_calls_get_current_commit_when_getting_source_info(
  __mock_add_padding_spaces,
  __mock_exists,
  __mock_get_current_commit,
  __mock_get_commit_branch,
  __mock_get_current_branch,
  __mock_is_tag
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
  __mock_get_current_commit.assert_called_once_with(dir=__SOURCE_PATH)

def test_calls_get_commit_branch_when_getting_source_info(
  __mock_add_padding_spaces,
  __mock_exists,
  __mock_get_current_commit,
  __mock_get_commit_branch,
  __mock_get_current_branch,
  __mock_is_tag
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
  __mock_get_commit_branch.assert_called_once_with(
    __mock_get_current_commit.return_value,
    dir=__SOURCE_PATH
  )

def test_calls_get_current_branch_when_getting_source_info(
  __mock_add_padding_spaces,
  __mock_exists,
  __mock_get_current_commit,
  __mock_get_commit_branch,
  __mock_get_current_branch,
  __mock_is_tag
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
  __mock_get_current_branch.assert_called_once_with(dir=__SOURCE_PATH)

def test_calls_is_tag_when_getting_source_info(
  __mock_add_padding_spaces,
  __mock_exists,
  __mock_get_current_commit,
  __mock_get_commit_branch,
  __mock_get_current_branch,
  __mock_is_tag
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
  __mock_is_tag.assert_called_once_with(dir=__SOURCE_PATH)

@pytest.mark.parametrize(
  "__mock_exists,__mock_is_tag,expected_info_right",
  [
    pytest.param(False, False, logger.yellow("Not found")),
    pytest.param(False, True, logger.yellow("Not found")),
    pytest.param(True, False, f"{__BRANCH_NAME} ({__COMMIT})"),
    pytest.param(True, True, f"{__TAG_NAME} ({__COMMIT})"),
  ],
  indirect=["__mock_exists", "__mock_is_tag"]
)
def test_returns_expected_source_info(
  expected_info_right,
  __mock_add_padding_spaces,
  __mock_exists,
  __mock_get_current_commit,
  __mock_get_commit_branch,
  __mock_get_current_branch,
  __mock_is_tag
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  source_info = version_executor._ModeVersionExecutor__get_source_info(__SOURCE)
  expected_info = f"{__SOURCE_LEFT_TEXT}{expected_info_right}"
  assert (
    source_info == expected_info
  ), get_assertion_message("source info", expected_info, source_info)

def test_calls_get_source_info_when_getting_sources_info(__mock_get_source_info):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_sources_info()
  __mock_get_source_info.assert_has_calls([
    call(source) for source in constants.XMIPP_SOURCES
  ])

def test_returns_expected_sources_info(__mock_get_source_info):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  sources_info = version_executor._ModeVersionExecutor__get_sources_info()
  expected_sources_info = '\n'.join([
    __mock_get_source_info(source) for source in constants.XMIPP_SOURCES
  ])
  assert (
    sources_info == expected_sources_info
  ), get_assertion_message("sources info", expected_sources_info, sources_info)

@pytest.mark.parametrize(
  "__mock_exists_sources,expected_result",
  [
    pytest.param([False, False], False),
    pytest.param([False, True], False),
    pytest.param([True, False], False),
    pytest.param([True, True], True)
  ],
  indirect=["__mock_exists_sources"]
)
def test_returns_expected_value_when_checking_if_all_sources_are_present(
  __mock_exists_sources,
  expected_result
):
  result = mode_version_executor._are_all_sources_present()
  assert (
    result == expected_result
  ), get_assertion_message("are all sources present value", expected_result, result)

def test_calls_logger_when_running_executor_in_short_format(__mock_logger):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = True
  version_executor.run()
  __mock_logger.assert_called_once_with(JSON_XMIPP_VERSION_NAME)

@pytest.mark.parametrize(
  "__mock_are_all_sources_present,__mock_exist_config_and_library_versions,"
  "__mock_is_tag,expected_title_version_type",
  [
    pytest.param(False, (False, False), False, __BRANCH_NAME),
    pytest.param(False, (False, False), True, 'release'),
    pytest.param(False, (False, True), False, __BRANCH_NAME),
    pytest.param(False, (False, True), True, 'release'),
    pytest.param(False, (True, False), False, __BRANCH_NAME),
    pytest.param(False, (True, False), True, 'release'),
    pytest.param(False, (True, True), False, __BRANCH_NAME),
    pytest.param(False, (True, True), True, 'release'),
    pytest.param(True, (False, False), False, __BRANCH_NAME),
    pytest.param(True, (False, False), True, 'release'),
    pytest.param(True, (False, True), False, __BRANCH_NAME),
    pytest.param(True, (False, True), True, 'release'),
    pytest.param(True, (True, False), False, __BRANCH_NAME),
    pytest.param(True, (True, False), True, 'release'),
    pytest.param(True, (True, True), False, __BRANCH_NAME),
    pytest.param(True, (True, True), True, 'release')
  ],
  indirect=[
    "__mock_are_all_sources_present",
    "__mock_exist_config_and_library_versions",
    "__mock_is_tag"
  ]
)
def test_calls_logger_when_running_executor_in_long_format(
  expected_title_version_type,
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_sources_info,
  __mock_exist_config_and_library_versions,
  __mock_get_library_versions_section,
  __mock_are_all_sources_present,
  __mock_get_configuration_warning_message
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  expected_title = f"Xmipp {JSON_XMIPP_VERSION_NUMBER} ({expected_title_version_type})"
  expected_lines = [
    f"{logger.bold(expected_title)}\n",
    __mock_get_dates_section(),
    f"{__mock_add_padding_spaces('System version: ')}{__mock_get_os_release_name()}",
    __mock_get_sources_info(),
  ]
  if __mock_exist_config_and_library_versions(paths.LIBRARY_VERSIONS_FILE):
    expected_lines.append(f"\n{__mock_get_library_versions_section()}")
  if (
    not __mock_exist_config_and_library_versions(paths.LIBRARY_VERSIONS_FILE) or
    not __mock_exist_config_and_library_versions(paths.CONFIG_FILE) or
    not __mock_are_all_sources_present()
  ):
    expected_lines.append(f"\n{__mock_get_configuration_warning_message()}")
  __mock_logger.assert_called_once_with("\n".join(expected_lines))

def test_calls_is_tag_when_running_executor_in_long_format(
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  __mock_is_tag.assert_called_once_with()

def test_calls_get_current_branch_when_running_executor_in_long_format_and_is_not_tag(
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  __mock_get_current_branch.assert_called_once_with()

def test_does_not_call_get_current_branch_when_running_executor_in_long_format_and_is_tag(
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  __mock_is_tag.return_value = True
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  __mock_get_current_branch.assert_not_called()

def test_calls_get_dates_section_when_running_executor_in_long_format(
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  __mock_get_dates_section.assert_called_once_with()

def test_calls_add_padding_spaces_when_running_executor_in_long_format(
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  __mock_add_padding_spaces.assert_called_once_with("System version: ")

def test_calls_get_os_release_name_when_running_executor_in_long_format(
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  __mock_get_os_release_name.assert_called_once_with()

def test_calls_get_source_info_when_running_executor_in_long_format(
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = False
  version_executor.run()
  expected_calls = [
    call(constants.XMIPP_CORE),
    call(constants.XMIPP_VIZ)
  ]
  __mock_get_source_info.assert_has_calls(expected_calls)
  assert (
    __mock_get_source_info.call_count == len(expected_calls)
  ), get_assertion_message("call count", __mock_get_source_info.call_count, len(expected_calls))

@pytest.mark.parametrize(
  "short_format",
  [
    pytest.param(False),
    pytest.param(True)
  ]
)
def test_returns_success_and_no_message_when_running_executor(
  short_format,
  __mock_logger,
  __mock_is_tag,
  __mock_get_current_branch,
  __mock_get_dates_section,
  __mock_add_padding_spaces,
  __mock_get_os_release_name,
  __mock_get_source_info
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor.short = short_format
  result = version_executor.run()
  assert (
    result == (0, "")
  ), get_assertion_message("executor run result", (0, ""), result)

def test_calls_os_path_exists_when_getting_library_versions_section(
  __mock_exists
):
  __mock_exists.return_value = False
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_library_versions_section()
  __mock_exists.assert_called_with(paths.LIBRARY_VERSIONS_FILE)

def test_calls_get_library_versions_from_cmake_file_when_getting_library_versions_section(
  __mock_get_library_versions_from_cmake_file
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_library_versions_section()
  __mock_get_library_versions_from_cmake_file.assert_called_with(paths.LIBRARY_VERSIONS_FILE)

def test_calls_add_padding_spaces_when_getting_library_versions_section(
  __mock_get_library_versions_from_cmake_file,
  __mock_add_padding_spaces
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  version_executor._ModeVersionExecutor__get_library_versions_section()
  __mock_add_padding_spaces.assert_has_calls([
    call(f"{library}: ") for library in __LIBRARIES_WITH_VERSIONS.keys()
  ])

@pytest.mark.parametrize(
  "__mock_get_library_versions_from_cmake_file,expected_versions_section",
  [
    pytest.param({}, ""),
    pytest.param(__LIBRARIES_WITH_VERSIONS, __LIBRARIES_WITH_VERSION_SECTION)
  ],
  indirect=["__mock_get_library_versions_from_cmake_file"]
)
def test_returns_expected_library_versions_section(
  __mock_get_library_versions_from_cmake_file,
  expected_versions_section,
  __mock_add_padding_spaces
):
  version_executor = ModeVersionExecutor(__CONTEXT.copy())
  versions_section = version_executor._ModeVersionExecutor__get_library_versions_section()
  assert (
    versions_section == expected_versions_section
  ), get_assertion_message("library versions section", expected_versions_section, versions_section)

def test_calls_logger_yellow_when_getting_configuration_warning_message(
  __mock_logger_yellow
):
  mode_version_executor._get_configuration_warning_message()
  __mock_logger_yellow.assert_has_calls([
    call("This project has not yet been configured, so some detectable dependencies have not been properly detected."),
    call("Run mode 'getSources' and then 'configBuild' to be able to show all detectable ones.")
  ])

def test_returns_expected_configuration_warning_message(
  __mock_logger_yellow
):
  warning_message = mode_version_executor._get_configuration_warning_message()
  expected_warning_message = '\n'.join([
    __mock_logger_yellow("This project has not yet been configured, so some detectable dependencies have not been properly detected."),
    __mock_logger_yellow("Run mode 'getSources' and then 'configBuild' to be able to show all detectable ones.")
  ])
  assert (
    warning_message == expected_warning_message
  ), get_assertion_message("configuration warning message", expected_warning_message, warning_message)

@pytest.fixture(params=[[True, True]])
def __mock_exists_init(request, __mock_exists):
  def __side_effect(path):
    config_file_exists = request.param[0]
    lib_file_exists = request.param[1]
    if path == paths.CONFIG_FILE:
      return config_file_exists
    elif path == paths.LIBRARY_VERSIONS_FILE:
      return lib_file_exists
    else:
      return False
  _ = __side_effect("non-existent") # To cover system case
  __mock_exists.side_effect = __side_effect
  yield __mock_exists

@pytest.fixture(params=[(True, True)])
def __mock_exist_config_and_library_versions(__mock_exists, request):
  def __side_effect(path):
    config_file_exists, library_version_file_exists = request.param
    if path == paths.CONFIG_FILE:
      return config_file_exists
    elif path == paths.LIBRARY_VERSIONS_FILE:
      return library_version_file_exists
    else:
      return False
  _ = __side_effect("non-existent") # To cover system case
  __mock_exists.side_effect = __side_effect
  yield __mock_exists

@pytest.fixture(params=[(True, True)])
def __mock_exists_sources(request, __mock_exists):
  def __side_effect(path):
    core_exists, viz_exists = request.param
    if path == paths.get_source_path(constants.XMIPP_CORE):
      return core_exists
    elif path == paths.get_source_path(constants.XMIPP_VIZ):
      return viz_exists
    else:
      return False
  _ = __side_effect("non-existent") # To cover system case
  __mock_exists.side_effect = __side_effect
  yield __mock_exists

@pytest.fixture(params=[True])
def __mock_exists(request):
  with patch("os.path.exists") as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __dummy_test_mode_executor():
  class TestExecutor(ModeExecutor):
    def run(self):
      return 0, ""
  TestExecutor(__CONTEXT.copy()).run() # For coverage
  return TestExecutor

@pytest.fixture
def __mock_left_text_len():
  with patch.object(
    ModeVersionExecutor,
    "_ModeVersionExecutor__LEFT_TEXT_LEN",
    new=__LEFT_TEXT_LEN
  ):
    yield

@pytest.fixture
def __mock_add_padding_spaces():
  with patch(
    "xmipp3_installer.installer.modes.mode_version_executor.ModeVersionExecutor._ModeVersionExecutor__add_padding_spaces"
  ) as mock_method:
    mock_method.side_effect = lambda text: text
    yield mock_method

@pytest.fixture
def __mock_get_current_commit():
  with patch(
    "xmipp3_installer.installer.handlers.git_handler.get_current_commit"
  ) as mock_method:
    mock_method.return_value = __COMMIT
    yield mock_method

@pytest.fixture
def __mock_get_commit_branch(__mock_is_tag):
  with patch(
    "xmipp3_installer.installer.handlers.git_handler.get_commit_branch"
  ) as mock_method:
    mock_method.return_value = __TAG_NAME if __mock_is_tag.return_value else __BRANCH_NAME
    yield mock_method

@pytest.fixture
def __mock_get_current_branch(__mock_is_tag):
  with patch(
    "xmipp3_installer.installer.handlers.git_handler.get_current_branch"
  ) as mock_method:
    mock_method.return_value = "HEAD" if __mock_is_tag.return_value else __BRANCH_NAME
    yield mock_method

@pytest.fixture(params=[False])
def __mock_is_tag(request):
  with patch(
    "xmipp3_installer.installer.handlers.git_handler.is_tag"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_get_source_info():
  with patch(
    "xmipp3_installer.installer.modes.mode_version_executor.ModeVersionExecutor._ModeVersionExecutor__get_source_info"
  ) as mock_method:
    mock_method.side_effect = lambda source: f"{source} info"
    yield mock_method

@pytest.fixture
def __mock_get_sources_info():
  with patch(
    "xmipp3_installer.installer.modes.mode_version_executor.ModeVersionExecutor._ModeVersionExecutor__get_sources_info"
  ) as mock_method:
    mock_method.return_value = "Source1: info\nSource2: info\n"
    yield mock_method

@pytest.fixture
def __mock_logger():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.__call__"
  ) as mock_method:
    yield mock_method

@pytest.fixture
def __mock_get_dates_section():
  with patch(
    "xmipp3_installer.installer.modes.mode_version_executor.ModeVersionExecutor._ModeVersionExecutor__get_dates_section"
  ) as mock_method:
    mock_method.return_value = "Release date: dd/mm/yyyy\nLast compilation: -"
    yield mock_method

@pytest.fixture
def __mock_get_os_release_name():
  with patch(
    "xmipp3_installer.api_client.assembler.installation_info_assembler.get_os_release_name"
  ) as mock_method:
    mock_method.return_value = __RELEASE_NAME
    yield mock_method

@pytest.fixture(params=[__LIBRARIES_WITH_VERSIONS])
def __mock_get_library_versions_from_cmake_file(request):
  with patch(
    "xmipp3_installer.installer.handlers.cmake.cmake_handler.get_library_versions_from_cmake_file"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_get_library_versions_section():
  with patch(
    "xmipp3_installer.installer.modes.mode_version_executor.ModeVersionExecutor._ModeVersionExecutor__get_library_versions_section"
  ) as mock_method:
    mock_method.return_value = __LIBRARIES_WITH_VERSION_SECTION
    yield mock_method

@pytest.fixture
def __mock_logger_yellow():
  with patch(
    "xmipp3_installer.application.logger.logger.Logger.yellow"
  ) as mock_method:
    mock_method.side_effect = lambda text: f"yellow-{text}-yellow"
    yield mock_method

@pytest.fixture(params=[False])
def __mock_are_all_sources_present(request):
  with patch(
    "xmipp3_installer.installer.modes.mode_version_executor._are_all_sources_present"
  ) as mock_method:
    mock_method.return_value = request.param
    yield mock_method

@pytest.fixture
def __mock_get_configuration_warning_message():
  with patch(
    "xmipp3_installer.installer.modes.mode_version_executor._get_configuration_warning_message"
  ) as mock_method:
    mock_method.return_value = "Warning message"
    yield mock_method
