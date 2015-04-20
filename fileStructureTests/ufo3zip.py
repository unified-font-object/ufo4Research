"""
UFO 3 Zip File System
-----------------

This implements an on-disk, compressed (zip) package
structure.
"""

import os
import tempfile
import shutil
import zipfile

from core.fileSystem import BaseFileSystem

class UFO3ZipFileSystem(BaseFileSystem):

	fileExtension = 'ufoz'

	def __init__(self, path):
		super(UFO3ZipFileSystem, self).__init__()
		self.needFileWrite = False
		self.path = path
		# first being lazy and allow to the archive to append files
		# this is not good and will lead to huge zip files...
		self.zip = zipfile.ZipFile(self.path, 'a')
		
	def close(self):
		self.zip.close()
		namelist = self.zip.namelist()
		hasDuplicates = len(namelist) != len(set(namelist))
		if hasDuplicates:
			temp = tempfile.mkstemp(suffix=".%s" % self.fileExtension)[1]
			inzip = zipfile.ZipFile(self.path, 'r')
			outzip = zipfile.ZipFile(temp, 'w')
			outzip.comment = inzip.comment
			for item in inzip.infolist():
				if item.filename not in outzip.namelist():
					data = inzip.read(item.filename)
					outzip.writestr(item, data, compress_type=item.compress_type)
			outzip.close()
			inzip.close()
			shutil.move(temp, self.path)
	
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
	from core.fileSystem import debugWriteFont, debugReadFont, debugRoundTripFont
	debugWriteFont(UFO3ZipFileSystem)
	debugReadFont(UFO3ZipFileSystem)
	diffs = debugRoundTripFont(UFO3ZipFileSystem)
	if diffs:
		print diffs
