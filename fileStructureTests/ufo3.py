import os
from core.fileSystem import AbstractFileSystem
from core.glyphTree import readGlyphFromTree

class UFO3FileSystem(AbstractFileSystem):

	def __init__(self, path):
		self.path = path
		self._layerContents = None
		super(UFO3FileSystem, self).__init__()
		if not os.path.exists(self.path):
			os.mkdir(path)

	# ------------
	# File Support
	# ------------

	def readBytesFromPath(self, relPath):
		path = os.path.join(self.path, relPath)
		if not os.path.exists(path):
			return None
		f = open(path, "rb")
		b = f.read()
		f.close()
		return b

	def writeBytesToPath(self, data, relPath):
		path = os.path.join(self.path, relPath)
		f = open(path, "wb")
		f.write(data)
		f.close()

	# ---------------
	# Top Level Files
	# ---------------

	def readMetaInfo(self):
		return self.readPlistFromPath("metainfo.plist")

	def writeMetaInfo(self, data):
		self.writePlistToPath(data, "metainfo.plist")

	def readFontInfo(self):
		return self.readPlistFromPath("fontinfo.plist")

	def writeFontInfo(self, data):
		self.writePlistToPath(data, "fontinfo.plist")

	def readGroups(self):
		return self.readPlistFromPath("groups.plist")

	def writeGroups(self, data):
		self.writePlistToPath(data, "groups.plist")

	def readKerning(self):
		return self.readPlistFromPath("kerning.plist")

	def writeKerning(self, data):
		self.writePlistToPath(data, "kerning.plist")

	def readFeatures(self):
		return self.readBytesFromPath("features.fea")

	def writeFeatures(self, data):
		self.writeBytesToPath(data, "features.fea")

	def readLib(self):
		return self.readPlistFromPath("lib.plist")

	def writeLib(self, data):
		self.writePlistToPath(data, "lib.plist")

	# -----------------
	# Layers and Glyphs
	# -----------------

	# layers

	def _readLayerContents(self):
		if self._layerContents is None:
			self._layerContents = self.readPlistFromPath("layercontents.plist")
		return self._layerContents

	def getLayerNames(self):
		layerContents = self._readLayerContents()
		layerNames = [layerName for layerName, directoryName in layerContents]
		return layerNames

	def getDefaultLayerName(self):
		layerContents = self._readLayerContents()
		for layerName, layerDirectory in layerContents:
			if layerDirectory == "glyphs":
				return layerName

	# glyph storage names

	def _getGlyphSetDirectory(self, layerName):
		layerContents = self._readLayerContents()
		for name, directory in layerContents:
			if name == layerName:
				break
		return directory

	def getGlyphStorageMapping(self, layerName):
		directory = self._getGlyphSetDirectory(layerName)
		path = os.path.join(directory, "contents.plist")
		return self.readPlistFromPath(path)

	# glyph tree

	def getGlyphTree(self, layerName, glyphName):
		storageName = self.getGlyphStorageName(layerName, glyphName)
		directory = self._getGlyphSetDirectory(layerName)
		path = os.path.join(directory, storageName)
		tree = self.getTreeForPath(path)
		return tree
