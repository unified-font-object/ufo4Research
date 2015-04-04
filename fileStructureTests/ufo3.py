import os
from core.fileSystem import BaseFileSystem
from core.glyphTree import readGlyphFromTree

class UFO3FileSystem(BaseFileSystem):

	def __init__(self, path):
		super(UFO3FileSystem, self).__init__()
		self.path = path
		if not os.path.exists(self.path):
			os.mkdir(path)

	# ------------
	# File Support
	# ------------

	# paths

	def joinLocations(self, location1, location2):
		return os.path.join(location1, location2)

	def splitLocation(self, location):
		return os.path.split(location)

	# bytes <-> location

	def readBytesFromLocation(self, location):
		path = os.path.join(self.path, location)
		if not os.path.exists(path):
			return None
		f = open(path, "rb")
		b = f.read()
		f.close()
		return b

	def writeBytesToLocation(self, data, location):
		parts = []
		b = location
		while 1:
			b, p = os.path.split(b)
			parts.insert(0, p)
			if not b:
				break
		for d in parts[:-1]:
			p = os.path.join(self.path, d)
			if not os.path.exists(p):
				os.mkdir(p)
		path = os.path.join(self.path, location)
		f = open(path, "wb")
		f.write(data)
		f.close()
