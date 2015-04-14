"""
UFO 3 Zip File System
-----------------

This implements an on-disk, compressed (zip) package
structure.
"""

import os
import zipfile

from core.fileSystem import BaseFileSystem

class UFO3ZipFileSystem(BaseFileSystem):

	def __init__(self, path):
		super(UFO3ZipFileSystem, self).__init__()
		self.needFileWrite = False
		self.path = path
		if os.path.exists(self.path):
			self.zip = zipfile.ZipFile(self.path, 'r')
		else:
			self.zip = zipfile.ZipFile(self.path, 'w')

	def close(self):
		self.zip.close()
	# ------------
	# File Support
	# ------------

	# locations

	def joinLocations(self, location1, *location2):
		return os.path.join(location1, *location2)

	def splitLocation(self, location):
		return os.path.split(location)

	# bytes <-> location

	def readBytesFromLocation(self, location):
		try:
			return self.zip.read(location)
		except KeyError:
			return None
		
	def writeBytesToLocation(self, data, location):
		self.zip.writestr(location, data, compress_type=zipfile.ZIP_DEFLATED)



if __name__ == "__main__":
	from core.fileSystem import debugWriteFont, debugReadFont
	debugWriteFont(UFO3ZipFileSystem, "ufoz")
	font = debugReadFont(UFO3ZipFileSystem, "ufoz")
