"""
Contains all version info required for Xmipp's installation process.
"""

#### THIS SHOULD BE LOCATED IN XMIPP'S REPOSITORY,
#### AND BE RETRIEVED FROM THERE

XMIPP = 'xmipp'
XMIPP_CORE = 'xmippCore'
XMIPP_VIZ = 'xmippViz'
XMIPP_PLUGIN = 'scipion-em-xmipp'

__LATEST_RELEASE_NUMBER = '3.XX.YY.0'
__LATEST_RELEASE_NAME = 'v3.XX.YY-TBD'
RELEASE_DATE = 'dd/mm/yyyy'
#####################################
DEVEL_BRANCHNAME = 'devel'					
MASTER_BRANCHNAME = 'master'				
																		
VERSION_KEY = 'version'							
VERNAME_KEY = 'vername'							
XMIPP_VERSIONS = {									
	XMIPP: {													
		VERSION_KEY: __LATEST_RELEASE_NUMBER,				
		VERNAME_KEY: __LATEST_RELEASE_NAME  
	},																
	XMIPP_CORE: {											
		VERSION_KEY: __LATEST_RELEASE_NUMBER,				
		VERNAME_KEY: __LATEST_RELEASE_NAME  
	}
}																		
#####################################
