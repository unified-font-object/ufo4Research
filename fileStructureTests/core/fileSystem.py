from xml.etree import cElementTree as ET
from plistTree import convertTreeToPlist


class FileSystemError(Exception): pass


class AbstractFileSystem(object):

	def __init__(self):
		self._glyphStorageNames = {}

	# ------------
	# File Support
	# ------------

	def getBytesForPath(self, relPath):
		raise NotImplementedError

	def getTreeForPath(self, relPath):
		data = self.getBytesForPath(relPath)
		if data is None:
			return None
		tree = ET.fromstring(data)
		return tree

	def readPlist(self, relPath):
		tree = self.getTreeForPath(relPath)
		if tree is None:
			return None
		try:
			return convertTreeToPlist(tree)
		except:
			raise FileSystemError("The file %s could not be read." % relPath)

	# ---------------
	# Top Level Files
	# ---------------

	def readMetaInfo(self):
		raise NotImplementedError

	def readFontInfo(self):
		raise NotImplementedError

	def readGroups(self):
		raise NotImplementedError

	def readKerning(self):
		raise NotImplementedError

	def readFeatures(self):
		raise NotImplementedError

	def readLib(self):
		raise NotImplementedError

	# -----------------
	# Layers and Glyphs
	# -----------------

	# layers

	def getLayerNames(self):
		raise NotImplementedError

	def getDefaultLayerName(self):
		raise NotImplementedError

	# glyph storage names

	def getGlyphStorageMapping(self, layerName):
		raise NotImplementedError

	def getGlyphStorageName(self, layerName, glyphName):
		if layerName not in self._glyphStorageNames:
			self._glyphStorageNames[layerName] = self.getGlyphStorageMapping(layerName)
		return self._glyphStorageNames[layerName][glyphName]

	def getGlyphNames(self, layerName):
		return self.getGlyphStorageMapping(layerName).keys()

	# glyph tree

	def getGlyphTree(self, layerName, glyphName):
		raise NotImplementedError
