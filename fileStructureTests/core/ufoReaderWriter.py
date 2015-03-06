from glyphTree import readGlyphFromTree


class UFOReaderWriterError(Exception): pass


class UFOReaderWriter(object):

	def __init__(self, fileSystem):
		self._fileSystem = fileSystem
		self.readMetaInfo()

	# metainfo

	def readMetaInfo(self):
		"""
		Read metainfo. Only used for internal operations.
		"""
		data = self._fileSystem.readMetaInfo()
		return data

	# groups

	def readGroups(self):
		"""
		Read groups. Returns a dict.
		"""
		groups = self._fileSystem.readGroups()
		if groups is None:
			return
		return groups

	# fontinfo

	def readInfo(self, info):
		"""
		Read fontinfo. It requires an object that allows
		setting attributes with names that follow the fontinfo
		version 3 specification. This will write the attributes
		defined in the file into the object.
		"""
		infoDict = self._fileSystem.readFontInfo()
		if infoDict is None:
			return
		for attr, value in infoDict.items():
			setattr(info, attr, value)

	# kerning

	def readKerning(self):
		"""
		Read kerning. Returns a dict.
		"""
		data = self._fileSystem.readKerning()
		if data is None:
			return
		kerning = {}
		for side1 in data:
			for side2 in data[side1]:
				value = data[side1][side2]
				kerning[side1, side2] = value
		return kerning

	# lib

	def readLib(self):
		"""
		Read lib. Returns a dict.
		"""
		data = self._fileSystem.readLib()
		if data is None:
			return
		return data

	# features

	def readFeatures(self):
		"""
		Read features. Returns a string.
		"""
		return self._fileSystem.readFeatures()

	# layers and glyphs

	def getLayerNames(self):
		"""
		Get the ordered layer names.
		"""
		return self._fileSystem.getLayerNames()

	def getDefaultLayerName(self):
		"""
		Get the default layer name.
		"""
		return self._fileSystem.getDefaultLayerName()

	def getGlyphNames(self, layerName):
		"""
		Return a list of glyph names.
		"""
		return self._fileSystem.getGlyphNames(layerName)

	def readGlyph(self, layerName, glyphName, glyphObject):
		"""
		Read a glyph from a layer.
		"""
		tree = self._fileSystem.getGlyphTree(layerName, glyphName)
		readGlyphFromTree(tree, glyphObject, glyphObject)
