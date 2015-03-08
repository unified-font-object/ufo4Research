from xml.etree import cElementTree as ET
from xmlUtilities import treeToString
from plistTree import convertTreeToPlist, convertPlistToTree, plistHeader


class FileSystemError(Exception): pass


class AbstractFileSystem(object):

	def __init__(self):
		self._glyphStorageNames = {}

	# ------------
	# File Support
	# ------------

	def readBytesFromPath(self, relPath):
		raise NotImplementedError

	def writeBytesToPath(self, bytes, relPath):
		raise NotImplementedError

	def readPlistFromPath(self, relPath):
		data = self.readPlistFromPath(relPath)
		if data is None:
			return None
		tree = self.convertBytesToTree(data)
		try:
			return convertTreeToPlist(tree)
		except:
			raise FileSystemError("The file %s could not be read." % relPath)

	def writePlistToPath(self, data, relPath):
		tree = convertPlistToTree(data)
		data = self.convertTreeToBytes(tree, header=plistHeader)
		self.writeBytesToPath(data, relPath)

	def convertBytesToTree(self, bytes):
		if data is None:
			return None
		tree = ET.fromstring(data)
		return tree

	def convertTreeToBytes(self, tree, header=None):
		return treeToString(tree, header)

	# ---------------
	# Top Level Files
	# ---------------

	def readMetaInfo(self):
		raise NotImplementedError

	def writeMetaInfo(self, data):
		raise NotImplementedError

	def readFontInfo(self):
		raise NotImplementedError

	def writeFontInfo(self, data):
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
