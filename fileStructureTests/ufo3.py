import os
from core.fileSystem import AbstractFileSystem
from core.glyphTree import readGlyphFromTree

class UFO3FileSystem(AbstractFileSystem):

	def __init__(self, path):
		self.path = path
		self._layerContents = None
		super(UFO3FileSystem, self).__init__()

	# ------------
	# File Support
	# ------------

	def getBytesForPath(self, relPath):
		path = os.path.join(self.path, relPath)
		if not os.path.exists(path):
			return None
		f = open(path, "rb")
		b = f.read()
		f.close()
		return b

	# ---------------
	# Top Level Files
	# ---------------

	def readMetaInfo(self):
		return self.readPlist("metainfo.plist")

	def readFontInfo(self):
		return self.readPlist("fontinfo.plist")

	def readGroups(self):
		return self.readPlist("groups.plist")

	def readKerning(self):
		return self.readPlist("kerning.plist")

	def readFeatures(self):
		return self.getBytesForPath("features.fea")

	def readLib(self):
		return self.readPlist("lib.plist")

	# -----------------
	# Layers and Glyphs
	# -----------------

	# layers

	def _readLayerContents(self):
		if self._layerContents is None:
			self._layerContents = self.readPlist("layercontents.plist")
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
		return self.readPlist(path)

	# glyph tree

	def getGlyphTree(self, layerName, glyphName):
		storageName = self.getGlyphStorageName(layerName, glyphName)
		directory = self._getGlyphSetDirectory(layerName)
		path = os.path.join(directory, storageName)
		tree = self.getTreeForPath(path)
		return tree
