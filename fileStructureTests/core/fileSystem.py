from collections import OrderedDict
from environment import ET
from xmlUtilities import treeToString
from plistTree import convertTreeToPlist, convertPlistToTree, plistHeader
from fileNames import userNameToFileName


class FileSystemError(Exception): pass


class BaseFileSystem(object):

	"""
	This implements the base file system functionality.


	# Locations and Names
	Locations are the place that given data should be stored.
	Names are the names of particular bits of data. For example,
	the glyph "A" in the default layer will have the name:

		A_.glif

	And the location:

		glyphs/A_.glif

	Locations are always relative to the top level of the UFO.


	# Trees
	All incoming data must be and all outgoing data will
	be instances of ElementTree Elements.

	# Subclasses
	Subclasses must override the base methods where indicated.
	Some methods may be overriden where indicated. All other
	methods must not be overriden.
	"""

	def __init__(self):
		self._haveReadLayerStorageMapping = False
		self._layerStorageMapping = OrderedDict()
		self._glyphStorageMapping = {}
		self._defaultLayerName = None

	def close(self):
		"""
		Close the file system. This must be called
		when any write operations are complete.

		Subclasses MAY override this method.
		"""
		pass

	# ------------
	# File Support
	# ------------

	# locations

	def joinLocations(self, location1, *location2):
		"""
		Return location1 and location2 joined by the
		appropriate separator. This behaves exactly
		like os.path.join.

		Subclasses MAY override this method.
		"""
		# taken from the Python Standard Library's posixpath.py
		a = location1
		p = location2
		path = a
		for b in p:
			if b.startswith('/'):
				path = b
			elif path == '' or path.endswith('/'):
				path +=  b
			else:
				path += '/' + b
		return path

	def splitLocation(self, location):
		"""
		Split location into a directory and basename.
		This behaves exactly like os.path.split.

		Subclasses MAY override this method.
		"""
		# taken from the Python Standard Library's posixpath.py
		p = location
		i = p.rfind('/') + 1
		head, tail = p[:i], p[i:]
		if head and head != '/'*len(head):
			head = head.rstrip('/')
		return head, tail

	# bytes <-> location

	def readBytesFromLocation(self, location):
		"""
		Read the data from the given location.
		If the location does not exist, this will return None.

		Subclasses MUST override this method.
		"""
		raise NotImplementedError

	def writeBytesToLocation(self, data, location):
		"""
		Write the given data into the given location.

		Subclasses MUST override this method.
		"""
		raise NotImplementedError

	# plist <-> location

	def readPlistFromLocation(self, location):
		"""
		Read a property list from the given location.

		Subclasses MUST NOT override this method.
		"""
		tree = self.readTreeFromLocation(location)
		if tree is None:
			return None
		try:
			return convertTreeToPlist(tree)
		except:
			raise FileSystemError("The file %s could not be read." % location)

	def writePlistToLocation(self, data, location):
		"""
		Write the given data into the given location
		in property list format.

		Subclasses MUST NOT override this method.
		"""
		tree = convertPlistToTree(data)
		self.writeTreeToLocation(tree, location, header=plistHeader)

	# tree <-> location

	def readTreeFromLocation(self, location):
		"""
		Read an XML tree from the given location.

		Subclasses MAY override this method.
		"""
		data = self.readBytesFromLocation(location)
		if data is None:
			return None
		tree = self.convertBytesToTree(data)
		return tree

	def writeTreeToLocation(self, tree, location, header=None):
		"""
		Write the given tree into the given location.
		If header is given, it will be inserted at the
		beginning of the XML string.

		Subclasses MAY override this method.
		"""
		data = self.convertTreeToBytes(tree, header)
		self.writeBytesToLocation(data, location)

	# bytes <-> tree

	def convertBytesToTree(self, data):
		"""
		Read an XML tree from the given string.

		Subclasses MUST NOT override this method.
		"""
		if data is None:
			return None
		tree = ET.fromstring(data)
		return tree

	def convertTreeToBytes(self, tree, header=None):
		"""
		Write the given tree to a string. If header
		is given, it will be inserted at the beginning
		of the XML string.

		Subclasses MUST NOT override this method.
		"""
		return treeToString(tree, header)

	# ---------------
	# Top Level Files
	# ---------------

	def readMetaInfo(self):
		"""
		Read the meta info to a tree.

		Subclasses MAY override this method.
		"""
		return self.readPlistFromLocation("metainfo.plist")

	def writeMetaInfo(self, tree):
		"""
		Write the meta info from a tree.

		Subclasses MAY override this method.
		"""
		self.writePlistToLocation(tree, "metainfo.plist")

	def readFontInfo(self):
		"""
		Read the font info to a tree.

		Subclasses MAY override this method.
		"""
		return self.readPlistFromLocation("fontinfo.plist")

	def writeFontInfo(self, tree):
		"""
		Write the font info from a tree.

		Subclasses MAY override this method.
		"""
		self.writePlistToLocation(tree, "fontinfo.plist")

	def readGroups(self):
		"""
		Read the groups to a tree.

		Subclasses MAY override this method.
		"""
		return self.readPlistFromLocation("groups.plist")

	def writeGroups(self, tree):
		"""
		Write the groups from a tree.

		Subclasses MAY override this method.
		"""
		self.writePlistToLocation(tree, "groups.plist")

	def readKerning(self):
		"""
		Read the kerning to a tree.

		Subclasses MAY override this method.
		"""
		return self.readPlistFromLocation("kerning.plist")

	def writeKerning(self, tree):
		"""
		Write the kerning from a tree.

		Subclasses MAY override this method.
		"""
		self.writePlistToLocation(tree, "kerning.plist")

	def readFeatures(self):
		"""
		Read the features to a string.

		Subclasses MAY override this method.
		"""
		return self.readBytesFromLocation("features.fea")

	def writeFeatures(self, tree):
		"""
		Write the features from a string.

		Subclasses MAY override this method.
		"""
		self.writeBytesToLocation(tree, "features.fea")

	def readLib(self):
		"""
		Read the lib to a tree.

		Subclasses MAY override this method.
		"""
		return self.readPlistFromLocation("lib.plist")

	def writeLib(self, tree):
		"""
		Write the lib from a tree.

		Subclasses MAY override this method.
		"""
		self.writePlistToLocation(tree, "lib.plist")

	# -----------------
	# Layers and Glyphs
	# -----------------

	# layers

	def readLayerContents(self):
		"""
		Read the layer contents mapping and return an OrderedDict of form:

			{
				layer name : storage name
			}

		Subclasses MAY override this method.
		"""
		raw = self.readPlistFromLocation("layercontents.plist")
		data = OrderedDict()
		if raw is not None:
			for layerName, storageName in raw:
				data[layerName] = storageName
		return data

	def writeLayerContents(self):
		"""
		Write the layer contents mapping.

		Subclasses MAY override this method.
		"""
		data = self.getLayerStorageMapping()
		data = [(k, v) for k, v in data.items()]
		self.writePlistToLocation(data, "layercontents.plist")

	def getLayerStorageMapping(self):
		"""
		Get the layer contents mapping as a dict of form:

			{
				layer name : storage name
			}

		Subclasses MUST NOT override this method.
		"""
		if not self._haveReadLayerStorageMapping:
			self._layerStorageMapping = self.readLayerContents()
			self._haveReadLayerStorageMapping = True
		return self._layerStorageMapping

	def getLayerStorageName(self, layerName):
		"""
		Get the storage name for the given layer name.
		If none is defined, one will be created using the
		UFO 3 user name to file name algorithm.

		Subclasses MUST NOT override this method.
		"""
		layerStorageMapping = self.getLayerStorageMapping()
		if layerName not in layerStorageMapping:
			if layerName == self.getDefaultLayerName():
				storageName = "glyphs"
			else:
				layerName = unicode(layerName)
				storageName = userNameToFileName(layerName, existing=layerStorageMapping.values(), prefix="glyphs.")
			layerStorageMapping[layerName] = storageName
		return layerStorageMapping[layerName]

	def getLayerNames(self):
		"""
		Get a list of all layer names, in order.

		Subclasses MUST NOT override this method.
		"""
		layerStorageMapping = self.getLayerStorageMapping()
		return layerStorageMapping.keys()

	def getDefaultLayerName(self):
		"""
		Get the default layer name.

		Subclasses MUST NOT override this method.
		"""
		if self._defaultLayerName is None:
			default = "public.default"
			for layerName, layerDirectory in self.getLayerStorageMapping():
				if layerDirectory == "glyphs":
					default = layerName
					break
			self._defaultLayerName = default
		return self._defaultLayerName

	def setDefaultLayerName(self, layerName):
		"""
		Set the default layer name.

		Subclasses MUST NOT override this method.
		"""
		self._defaultLayerName = layerName

	# glyphs

	def readGlyphSetContents(self, layerName):
		"""
		Read the glyph set contents mapping for the given layer name.

		Subclasses MAY override this method.
		"""
		layerDirectory = self.getLayerStorageName(layerName)
		path = self.joinLocations(layerDirectory, "contents.plist")
		data = self.readPlistFromLocation(path)
		if data is None:
			data = {}
		return data

	def writeGlyphSetContents(self, layerName):
		"""
		Write the glyph set contents mapping for the given layer name.

		Subclasses MAY override this method.
		"""
		layerDirectory = self.getLayerStorageName(layerName)
		path = self.joinLocations(layerDirectory, "contents.plist")
		data = self.getGlyphStorageMapping(layerName)
		self.writePlistToLocation(data, path)

	def getGlyphStorageMapping(self, layerName):
		"""
		Get the glyph set contents mapping for the given layer name.

		Subclasses MUST NOT override this method.
		"""
		if self._glyphStorageMapping.get(layerName) is None:
			data = self.readGlyphSetContents(layerName)
			self._glyphStorageMapping[layerName] = data
		return self._glyphStorageMapping[layerName]

	def getGlyphStorageName(self, layerName, glyphName):
		"""
		Get the glyph storage name for the given layer name and glyph name.
		If none is defined, one will be created using the
		UFO 3 user name to file name algorithm.

		Subclasses MUST NOT override this method.
		"""
		glyphStorageMapping = self.getGlyphStorageMapping(layerName)
		if glyphName not in glyphStorageMapping:
			storageName = userNameToFileName(unicode(glyphName), existing=glyphStorageMapping.values(), suffix=".glif")
			glyphStorageMapping[glyphName] = storageName
		return glyphStorageMapping[glyphName]

	def getGlyphNames(self, layerName):
		"""
		Get a list of glyph names for layer name.

		Subclasses MUST NOT override this method.
		"""
		return self.getGlyphStorageMapping(layerName).keys()

	def readGlyph(self, layerName, glyphName):
		"""
		Read a glyph with the given name from the layer
		with the given layer name.

		Subclasses MAY override this method.
		"""
		layerStorageName = self.getLayerStorageName(layerName)
		glyphStorageName = self.getGlyphStorageName(layerName, glyphName)
		path = self.joinLocations(layerStorageName, glyphStorageName)
		tree = self.readTreeFromLocation(path)
		return tree

	def writeGlyph(self, layerName, glyphName, tree):
		"""
		Write a glyph with the given name to the layer
		with the given layer name from the given tree.

		Subclasses MAY override this method.
		"""
		layerStorageName = self.getLayerStorageName(layerName)
		glyphStorageName = self.getGlyphStorageName(layerName, glyphName)
		path = self.joinLocations(layerStorageName, glyphStorageName)
		self.writeTreeToLocation(tree, path)


# ---------
# Debugging
# ---------

def _makeTestPath(fileSystemClass, fileExtension):
	import os
	fileName = "ufo4-debug-%s.%s" % (fileSystemClass.__name__, fileExtension)
	path = os.path.join("~", "desktop", fileName)
	path = os.path.expanduser(path)
	return path


def debugWriteFont(fileSystemClass, fileExtension):
	"""
	This function will write a basic font file
	with the given file system class. It will
	be written to the following path:

		~/desktop/ufo4-debug-[file system class name].[file extension]

	This should only be used for debugging when
	creating a subclass of BaseFileSystem.
	"""
	import os
	import shutil
	from ufoReaderWriter import UFOReaderWriter
	from fonts import compileFont

	font = compileFont("file structure building test")

	path = _makeTestPath(fileSystemClass, fileExtension)
	if os.path.exists(path):
		if os.path.isdir(path):
			shutil.rmtree(path)
		else:
			os.remove(path)

	fileSystem = fileSystemClass(path)

	writer = UFOReaderWriter(fileSystem)
	writer.writeMetaInfo()
	writer.writeInfo(font.info)
	writer.writeGroups(font.groups)
	writer.writeKerning(font.kerning)
	writer.writeLib(font.lib)
	writer.writeFeatures(font.features)
	for layerName, layer in sorted(font.layers.items()):
		for glyphName in sorted(layer.keys()):
			glyph = layer[glyphName]
			writer.writeGlyph(layerName, glyphName, glyph)
		writer.writeGlyphSetContents(layerName)
	writer.writeLayerContents()
	writer.close()

def debugReadFont(fileSystemClass, fileExtension):
	"""
	This function will read a font file with
	the given file system class. It expects
	a file to be located at the following path:

		~/desktop/ufo4-debug-[file system class name].[file extension]

	This should only be used for debugging when
	creating a subclass of BaseFileSystem.
	"""
	from ufoReaderWriter import UFOReaderWriter
	from objects import Font

	path = _makeTestPath(fileSystemClass, fileExtension)

	fileSystem = fileSystemClass(path)

	font = Font()
	reader = UFOReaderWriter(fileSystem)
	reader.readMetaInfo()
	reader.readInfo(font.info)
	font.groups = reader.readGroups()
	font.kerning = reader.readKerning()
	font.lib = reader.readLib()
	font.features = reader.readFeatures()
	font.loadLayers(reader)
	for layer in font.layers.values():
		for glyph in layer:
			pass
	return font
