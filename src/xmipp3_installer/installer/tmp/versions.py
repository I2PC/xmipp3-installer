"""
Contains all version info required for Xmipp's installation process.
"""

from xmipp3_installer.installer import constants

#### THIS SHOULD BE LOCATED IN XMIPP'S REPOSITORY,
#### AND BE RETRIEVED FROM THERE

__LATEST_RELEASE_NUMBER = '3.XX.YY.0'
__LATEST_RELEASE_NAME = 'v3.XX.YY-TBD'
RELEASE_DATE = 'dd/mm/yyyy'
#####################################
VERSION_KEY = 'version'							
VERNAME_KEY = 'vername'							
XMIPP_VERSIONS = {									
	constants.XMIPP: {													
		VERSION_KEY: __LATEST_RELEASE_NUMBER,				
		VERNAME_KEY: __LATEST_RELEASE_NAME  
	}
}																		
#####################################
