# ***************************************************************************
# * Authors:		Alberto García (alberto.garcia@cnb.csic.es)
# *							Martín Salinas (martin.salinas@cnb.csic.es)
# *
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307 USA
# *
# * All comments concerning this program package may be sent to the
# * e-mail address 'scipion@cnb.csic.es'
# ***************************************************************************/

"""
Module containing all functions needed for the metric's API request.
"""

# Self imports
from .utils import runJob
from .constants import UNKNOWN_VALUE
	
####################### UTILS FUNCTIONS #######################
def getOSReleaseName() -> str:
	"""
	### This function returns the name of the current system OS release.

	#### Returns:
	- (str): OS release name.
	"""
	# Initializing default release name 
	releaseName = UNKNOWN_VALUE
	
	# Text around release name
	textBefore = 'PRETTY_NAME="'
	textAfter = '"\n'

	# Obtaining os release name
	retCode, name = runJob('cat /etc/os-release')

	# Look for release name if command did not fail
	if retCode == 0:
		# Find release name's line in command output
		targetStart = name.find(textBefore)
		if targetStart != 1:
			# Search end of release name's line
			nameEnd = name[targetStart:].find(textAfter)

			# Calculate release name's start index
			nameStart = targetStart + len(textBefore)
			if nameEnd != -1 and nameStart != nameEnd:
				# If everything was correctly found and string is 
				# not empty, extract release name
				releaseName = name[nameStart:nameEnd]

	# Return release name
	return releaseName
