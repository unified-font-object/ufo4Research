from glyphTree import readGlyphFromTree, writeGlyphToTree


class UFOReaderWriterError(Exception): pass


class UFOReaderWriter(object):

	def __init__(self, fileSystem):
		self._fileSystem = fileSystem

	def close(self):
		"""
		Close this object. This must be called when the
		work this object was needed to perform is complete.
		"""
		self._fileSystem.close()

	# metainfo

	def readMetaInfo(self):
		"""
		Read metainfo. Only used for internal operations.
		"""
		data = self._fileSystem.readMetaInfo()
		return data

	def writeMetaInfo(self):
		"""
		Write metainfo.
		"""
		data = dict(
			creator="org.unifiedfontobject.ufo4Tests.UFOReaderWriter",
			formatVersion="4"
		)
		self._fileSystem.writeMetaInfo(data)

	# groups

	def readGroups(self):
		"""
		Read groups. Returns a dict.
		"""
		groups = self._fileSystem.readGroups()
		if groups is None:
			return
		return groups

	def writeGroups(self, data):
		"""
		Write groups.
		"""
		if data:
			self._fileSystem.writeGroups(data)

	# fontinfo

	def readInfo(self, info):
		"""
		Read fontinfo.
		"""
		infoDict = self._fileSystem.readFontInfo()
		if infoDict is None:
			return
		for attr, value in infoDict.items():
			setattr(info, attr, value)

	def writeInfo(self, info):
		"""
		Write info.
		"""
		infoDict = {}
		for attr in fontInfoAttributes:
			if hasattr(info, attr):
				value = getattr(info, attr)
				if value is None:
					continue
				infoDict[attr] = value
		if infoDict:
			self._fileSystem.writeFontInfo(infoDict)

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

	def writeKerning(self, data):
		"""
		Write kerning.
		"""
		kerning = {}
		for (side1, side2), value in data.items():
			if not side1 in kerning:
				kerning[side1] = {}
			kerning[side1][side2] = value
		if kerning:
			self._fileSystem.writeKerning(kerning)

	# lib

	def readLib(self):
		"""
		Read lib. Returns a dict.
		"""
		data = self._fileSystem.readLib()
		if data is None:
			return
		return data

	def writeLib(self, data):
		"""
		Write lib.
		"""
		if data:
			self._fileSystem.writeLib(data)

	# features

	def readFeatures(self):
		"""
		Read features. Returns a string.
		"""
		return self._fileSystem.readFeatures()

	def writeFeatures(self, data):
		"""
		Write features.
		"""
		self._fileSystem.writeFeatures(data)

	# layers and glyphs

	def writeLayerContents(self):
		"""
		Write the layer contents.
		"""
		self._fileSystem.writeLayerContents()

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

	def writeGlyphSetContents(self, layerName):
		"""
		Write the glyph set contents for the given layer name.
		"""
		self._fileSystem.writeGlyphSetContents(layerName)

	def getGlyphNames(self, layerName):
		"""
		Return a list of glyph names.
		"""
		return self._fileSystem.getGlyphNames(layerName)

	def readGlyph(self, layerName, glyphName, glyphObject):
		"""
		Read a glyph from a layer.
		"""
		tree = self._fileSystem.readGlyph(layerName, glyphName)
		readGlyphFromTree(tree, glyphObject, glyphObject)

	def writeGlyph(self, layerName, glyphName, glyphObject):
		"""
		Write a glyph from a layer.
		"""
		tree = writeGlyphToTree(glyphObject)
		self._fileSystem.writeGlyph(layerName, glyphName, tree)


fontInfoAttributes = """
familyName
styleName
styleMapFamilyName
styleMapStyleName
versionMajor
versionMinor
year
copyright
trademark
unitsPerEm
descender
xHeight
capHeight
ascender
italicAngle
note
openTypeHeadCreated
openTypeHeadLowestRecPPEM
openTypeHeadFlags
openTypeHheaAscender
openTypeHheaDescender
openTypeHheaLineGap
openTypeHheaCaretSlopeRise
openTypeHheaCaretSlopeRun
openTypeHheaCaretOffset
openTypeNameDesigner
openTypeNameDesignerURL
openTypeNameManufacturer
openTypeNameManufacturerURL
openTypeNameLicense
openTypeNameLicenseURL
openTypeNameVersion
openTypeNameUniqueID
openTypeNameDescription
openTypeNamePreferredFamilyName
openTypeNamePreferredSubfamilyName
openTypeNameCompatibleFullName
openTypeNameSampleText
openTypeNameWWSFamilyName
openTypeNameWWSSubfamilyName
openTypeOS2WidthClass
openTypeOS2WeightClass
openTypeOS2Selection
openTypeOS2VendorID
openTypeOS2Panose
openTypeOS2FamilyClass
openTypeOS2UnicodeRanges
openTypeOS2CodePageRanges
openTypeOS2TypoAscender
openTypeOS2TypoDescender
openTypeOS2TypoLineGap
openTypeOS2WinAscent
openTypeOS2WinDescent
openTypeOS2Type
openTypeOS2SubscriptXSize
openTypeOS2SubscriptYSize
openTypeOS2SubscriptXOffset
openTypeOS2SubscriptYOffset
openTypeOS2SuperscriptXSize
openTypeOS2SuperscriptYSize
openTypeOS2SuperscriptXOffset
openTypeOS2SuperscriptYOffset
openTypeOS2StrikeoutSize
openTypeOS2StrikeoutPosition
openTypeVheaVertTypoAscender
openTypeVheaVertTypoDescender
openTypeVheaVertTypoLineGap
openTypeVheaCaretSlopeRise
openTypeVheaCaretSlopeRun
openTypeVheaCaretOffset
postscriptFontName
postscriptFullName
postscriptSlantAngle
postscriptUniqueID
postscriptUnderlineThickness
postscriptUnderlinePosition
postscriptIsFixedPitch
postscriptBlueValues
postscriptOtherBlues
postscriptFamilyBlues
postscriptFamilyOtherBlues
postscriptStemSnapH
postscriptStemSnapV
postscriptBlueFuzz
postscriptBlueShift
postscriptBlueScale
postscriptForceBold
postscriptDefaultWidthX
postscriptNominalWidthX
postscriptWeightName
postscriptDefaultCharacter
postscriptWindowsCharacterSet
macintoshFONDFamilyID
macintoshFONDName
versionMinor
unitsPerEm
openTypeHeadLowestRecPPEM
openTypeHheaAscender
openTypeHheaDescender
openTypeHheaLineGap
openTypeHheaCaretOffset
openTypeOS2Panose
openTypeOS2TypoAscender
openTypeOS2TypoDescender
openTypeOS2TypoLineGap
openTypeOS2WinAscent
openTypeOS2WinDescent
openTypeOS2SubscriptXSize
openTypeOS2SubscriptYSize
openTypeOS2SubscriptXOffset
openTypeOS2SubscriptYOffset
openTypeOS2SuperscriptXSize
openTypeOS2SuperscriptYSize
openTypeOS2SuperscriptXOffset
openTypeOS2SuperscriptYOffset
openTypeOS2StrikeoutSize
openTypeOS2StrikeoutPosition
openTypeGaspRangeRecords
openTypeNameRecords
openTypeVheaVertTypoAscender
openTypeVheaVertTypoDescender
openTypeVheaVertTypoLineGap
openTypeVheaCaretOffset
woffMajorVersion
woffMinorVersion
woffMetadataUniqueID
woffMetadataVendor
woffMetadataCredits
woffMetadataDescription
woffMetadataLicense
woffMetadataCopyright
woffMetadataTrademark
woffMetadataLicensee
woffMetadataExtensions
guidelines
""".strip().split()