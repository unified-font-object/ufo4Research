"""
Single XML File System
----------------------

This implements one big XML file. This is the schema:

<font>
	<fontinfo> plist </fontinfo>
	<groups> plist </groups>
	<kerning> plist </kerning>
	<lib> plist </lib>
	<features> text </features>
	<glyphs name="text">
		<glyph name="text"> glif </glyph>
	</glyphs>
</font>
"""

import os
from collections import OrderedDict
from core.environment import ET
from core.fileSystem import BaseFileSystem
from core.plistTree import convertPlistToTree

class SingleXMLFileSystem(BaseFileSystem):

	fileExtension = 'xml'

	def __init__(self, path):
		super(SingleXMLFileSystem, self).__init__()
		self.needFileWrite = False
		self.path = path
		if os.path.exists(path):
			f = open(path, "rb")
			data = f.read()
			f.close()
			self.tree = ET.fromstring(data)
		else:
			self.tree = ET.Element("font")

	def close(self):
		if self.needFileWrite:
			_indent(self.tree)
			data = ET.tostring(self.tree)
			f = open(self.path, "wb")
			f.write(data)
			f.close()
		self.needFileWrite = False

	# ------------
	# File Support
	# ------------

	# bytes <-> location

	"""
	Raw bytes are not stored in this format.
	Everything is wrapped in a tree and is thus
	handled by the tree reading and writing methods.
	"""

	def readBytesFromLocation(self, location):
		raise NotImplementedError

	def writeBytesToLocation(self, data, location):
		raise NotImplementedError

	# tree <-> location

	"""
	Tree read and write are overriden here to
	implement the custom XML file structure that
	encapsulates the font data.
	"""

	_locationTags = {
		"fontinfo.plist" : "fontinfo",
		"groups.plist" : "groups",
		"kerning.plist" : "kerning",
		"features.fea" : "features",
		"lib.plist" : "lib",
	}

	def readTreeFromLocation(self, location):
		if isinstance(location, dict):
			if location["type"] == "glyph":
				return self._readGlyphFromLayer(location)
		else:
			tag = self._locationTags[location]
			element = self.tree.find(tag)
			return element

	def _readGlyphFromLayer(self, location):
		layerName = location["layer"]
		glyphName = location["name"]
		path = "glyphs[@name='%s']/glyph[@name='%s']" % (layerName, glyphName)
		return self.tree.find(path)

	def writeTreeToLocation(self, tree, location, header=None):
		self.needFileWrite = True
		if isinstance(location, dict):
			if location["type"] == "glyph":
				self._writeGlyphToLayer(tree, location)
		else:
			tag = self._locationTags[location]
			tree.tag = tag
			existing = self.tree.find(tag)
			if existing is not None:
				index = self.tree.getchildren().index(existing)
				self.tree.remove(existing)
				self.tree.insert(index, tree)
			else:
				self.tree.append(tree)

	def _writeGlyphToLayer(self, tree, location):
		layerName = location["layer"]
		glyphName = location["name"]
		# find the layer element
		found = False
		path = "glyphs[@name='%s']" % layerName
		layerElement = self.tree.find(path)
		if layerElement is None:
			layerElement = ET.Element("glyphs")
			layerElement.attrib["name"] = layerName
			self.tree.append(layerElement)
		# store the glyph
		tree.tag = "glyph"
		existing = layerElement.find("glyph[@name='%s']" % glyphName)
		if existing is not None:
			index = layerElement.getchildren().index(existing)
			layerElement.remove(existing)
			layerElement.insert(index, tree)
		else:
			layerElement.append(tree)

	# ---------------
	# Top Level Files
	# ---------------

	"""
	The metainfo.plist data is stored as the attributes
	of the root element instead of a separate element.
	"""

	def readMetaInfo(self):
		tree = convertPlistToTree(self.tree.attrib)
		return tree

	def writeMetaInfo(self, tree):
		attrib = {
			k : str(v) for k, v in tree.items()
		}
		self.tree.attrib.update(attrib)

	"""
	The contents of features.fea are wrapped in
	a <features> element.
	"""

	def readFeatures(self):
		tree = self.readTreeFromLocation("features.fea")
		if tree is None:
			return ""
		return tree.text

	def writeFeatures(self, tree):
		# convert to an element
		element = ET.Element("features")
		element.text = tree
		self.writeTreeToLocation(tree, "features.fea")

	# -----------------
	# Layers and Glyphs
	# -----------------

	"""
	layercontents.plist is implied.
	"""

	def readLayerContents(self):
		layerContents = OrderedDict()
		for layerElement in self.tree.findall("glyphs"):
			layerName = layerElement.attrib["name"]
			layerContents[layerName] = layerName
		return layerContents

	def writeLayerContents(self):
		pass

	"""
	glyphs*/contents.plist is implied.
	"""

	def readGlyphSetContents(self, layerName):
		glyphSetContents = {}
		layerElement = self.tree.find("glyphs[@name='%s']" % layerName)
		if layerElement is not None:
			for glyphElement in layerElement.findall("glyph"):
				glyphName = glyphElement.attrib["name"]
				glyphSetContents[glyphName] = glyphName
		return glyphSetContents

	def writeGlyphSetContents(self, layerName):
		pass

	def readGlyph(self, layerName, glyphName):
		path = dict(type="glyph", layer=layerName, name=glyphName)
		tree = self.readTreeFromLocation(path)
		return tree

	def writeGlyph(self, layerName, glyphName, tree):
		path = dict(type="glyph", layer=layerName, name=glyphName)
		self.writeTreeToLocation(tree, path)


def _indent(elem, whitespace="\t", level=0):
	# taken from http://effbot.org/zone/element-lib.htm#prettyprint
	i = "\n" + level * whitespace
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + whitespace
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			_indent(elem, whitespace, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

if __name__ == "__main__":
	from core.fileSystem import debugWriteFont, debugReadFont
	debugWriteFont(SingleXMLFileSystem)
	font = debugReadFont(SingleXMLFileSystem)
