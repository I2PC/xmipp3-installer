from xmipp3_installer.application.logger.logger import logger

XMIPP_DOCS = "More details on the Xmipp documentation portal: https://i2pc.github.io/docs/"
IO_ERROR_NO_FORMAT = f"""Error 7: Input/output error.
This error can be caused by the installer not being able to read/write/create/delete a file. Check your permissions on this directory.
{XMIPP_DOCS}"""
IO_ERROR = logger.red(IO_ERROR_NO_FORMAT)
