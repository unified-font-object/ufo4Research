from environment import ET
from plistTree import convertTreeToPlist, convertPlistToTree

class GlyphTreeError(Exception): pass

# -------------
# Glyph Reading
# -------------

def readGlyphFromTree(tree, glyphObject=None, pointPen=None, formatVersions=(2)):
	readGlyphFromTreeFormat2(tree=tree, glyphObject=glyphObject, pointPen=pointPen)

def readGlyphFromTreeFormat2(tree, glyphObject=None, pointPen=None):
	# get the name
	_readName(glyphObject, tree)
	# populate the sub elements
	unicodes = []
	guidelines = []
	anchors = []
	haveSeenAdvance = haveSeenImage = haveSeenOutline = haveSeenLib = haveSeenNote = False
	identifiers = set()
	for element in tree:
		tag = element.tag
		if tag == "outline":
			attrib = element.attrib
			haveSeenOutline = True
			if pointPen is not None:
				buildOutlineFormat2(glyphObject, pointPen, element, identifiers)
		elif glyphObject is None:
			continue
		elif tag == "advance":
			haveSeenAdvance = True
			_readAdvance(glyphObject, element)
		elif tag == "unicode":
			try:
				attrib = element.attrib
				v = attrib.get("hex", "undefined")
				v = int(v, 16)
				if v not in unicodes:
					unicodes.append(v)
			except ValueError:
				raise GlyphTreeError("Illegal value for hex attribute of unicode element.")
		elif tag == "guideline":
			attrib = element.attrib
			for attr in ("x", "y", "angle"):
				if attr in attrib:
					attrib[attr] = _number(attrib[attr])
			guidelines.append(attrib)
		elif tag == "anchor":
			attrib = element.attrib
			for attr in ("x", "y"):
				if attr in attrib:
					attrib[attr] = _number(attrib[attr])
			anchors.append(attrib)
		elif tag == "image":
			haveSeenImage = True
			_readImage(glyphObject, element)
		elif tag == "note":
			haveSeenNote = True
			_readNote(glyphObject, element)
		elif tag == "lib":
			haveSeenLib = True
			_readLib(glyphObject, element)
		else:
			raise GlyphTreeError("Unknown element in GLIF: %s" % tag)
	# set the collected unicodes
	if unicodes:
		_relaxedSetattr(glyphObject, "unicodes", unicodes)
	# set the collected guidelines
	if guidelines:
		_relaxedSetattr(glyphObject, "guidelines", guidelines)
	# set the collected anchors
	if anchors:
		_relaxedSetattr(glyphObject, "anchors", anchors)

def _readName(glyphObject, element):
	glyphName = element.attrib.get("name")
	if glyphName and glyphObject is not None:
		_relaxedSetattr(glyphObject, "name", glyphName)

def _readAdvance(glyphObject, element):
	attrib = element.attrib
	width = _number(attrib.get("width", 0))
	_relaxedSetattr(glyphObject, "width", width)
	height = _number(attrib.get("height", 0))
	_relaxedSetattr(glyphObject, "height", height)

def _readNote(glyphObject, element):
	rawNote = element.text
	lines = rawNote.split("\n")
	lines = [line.strip() for line in lines]
	note = "\n".join(lines)
	_relaxedSetattr(glyphObject, "note", note)

def _readLib(glyphObject, element):
	from plist import convertTreeToPlist
	assert len(element) == 1
	lib = convertTreeToPlist(element[0])
	if lib is None:
		lib = {}
	_relaxedSetattr(glyphObject, "lib", lib)

def _readImage(glyphObject, element):
	imageData = element.attrib
	for attr, default in _transformationInfo:
		value = default
		if attr in imageData:
			value = imageData[attr]
		imageData[attr] = _number(value)
	_relaxedSetattr(glyphObject, "image", imageData)

# ----------------
# GLIF to PointPen
# ----------------

def buildOutlineFormat2(glyphObject, pen, tree, identifiers):
	anchors = []
	for element in tree:
		tag = element.tag
		if tag == "contour":
			_buildOutlineContourFormat2(pen, element, identifiers)
		elif tag == "component":
			_buildOutlineComponentFormat2(pen, element, identifiers)
		else:
			raise GlyphTreeError("Unknown element in outline element: %s" % tag)

def _buildOutlineContourFormat2(pen, tree, identifiers):
	attrib = tree.attrib
	identifier = attrib.get("identifier")
	if identifier is not None:
		identifiers.add(identifier)
	pen.beginPath(identifier=identifier)
	for element in tree:
		_buildOutlinePointsFormat2(pen, element, identifiers)
	pen.endPath()

def _buildOutlinePointsFormat2(pen, element, identifiers):
	attrib = element.attrib
	x = _number(attrib["x"])
	y = _number(attrib["y"])
	segmentType = attrib.get("type")
	smooth = attrib.get("smooth")
	if smooth is not None:
		smooth = smooth == "yes"
	else:
		smooth = False
	name = attrib.get("name")
	identifier = attrib.get("identifier")
	pen.addPoint((x, y), segmentType=segmentType, smooth=smooth, name=name, identifier=identifier)

def _buildOutlineComponentFormat2(pen, element, identifiers):
	if len(element):
		raise GlyphTreeError("Unknown child elements of component element.")
	attrib = element.attrib
	baseGlyphName = attrib.get("base")
	transformation = []
	for attr, default in _transformationInfo:
		value = attrib.get(attr)
		if value is None:
			value = default
		else:
			value = _number(value)
		transformation.append(value)
	identifier = attrib.get("identifier")
	pen.addComponent(baseGlyphName, tuple(transformation), identifier=identifier)

# -------------
# Glyph Writing
# -------------

def writeGlyphToTree(glyph):
	tree = ET.Element("glyph")
	tree.attrib["name"] = glyph.name
	tree.attrib["format"] = "2"
	_writeAdvance(glyph, tree)
	_writeUnicodes(glyph, tree)
	_writeNote(glyph, tree)
	_writeImage(glyph, tree)
	_writeGuidelines(glyph, tree)
	_writeAnchors(glyph, tree)
	_writeOutline(glyph, tree)
	_writeLib(glyph, tree)
	return tree

def _writeAdvance(glyph, tree):
	width = glyph.width
	height = glyph.height
	if width or height:
		element = ET.Element("advance")
		if width:
			element.attrib["width"] = str(width)
		if height:
			element.attrib["height"] = str(height)
		tree.append(element)

def _writeUnicodes(glyph, tree):
	for code in glyph.unicodes:
		hexCode = hex(code)[2:].upper()
		if len(hexCode) < 4:
			hexCode = "0" * (4 - len(hexCode)) + hexCode
		element = ET.Element("unicode")
		element.attrib["hex"] = hexCode
		tree.append(element)

def _writeNote(glyph, tree):
	note = glyph.note
	if note:
		element = ET.Element("note")
		element.text = note
		tree.append(element)

def _writeImage(glyph, tree):
	if not glyph.image:
		return
	element = ET.Element("image")
	element.attrib.update(glyph.image)
	tree.append(image)

def _writeGuidelines(glyph, tree):
	for guideline in glyph.guidelines:
		data = {}
		for key, value in guideline.items():
			data[key] = str(value)
		element = ET.Element("guideline")
		tree.append(guideline)

def _writeAnchors(glyph, tree):
	for anchor in glyph.anchors:
		element = ET.Element("anchor")
		element.attrib.update(anchor)
		tree.append(element)

def _writeLib(glyph, tree):
	if glyph.lib:
		element = convertPlistToTree(glyph.lib)
		tree.append(element)

def _writeOutline(glyph, tree):
	element = ET.Element("outline")
	_writeContours(glyph, element)
	_writeComponents(glyph, element)
	tree.append(element)

def _writeContours(glyph, tree):
	for contour in glyph.contours:
		contourElement = ET.Element("contour")
		if contour.identifier:
			contourElement.attrib["identifier"] = contour.identifier
		for point in contour:
			(x, y), segmentType, smooth, name, identifier = point
			pointElement = ET.Element("point")
			pointElement.attrib["x"] = str(x)
			pointElement.attrib["y"] = str(y)
			if segmentType:
				pointElement.attrib["type"] = segmentType
			if smooth:
				pointElement.attrib["smooth"] = "yes"
			if identifier:
				pointElement.attrib["identifier"] = identifier
			contourElement.append(pointElement)
		tree.append(contourElement)

_transformationInfo = [
	# field name, default value
	("xScale",    1),
	("xyScale",   0),
	("yxScale",   0),
	("yScale",    1),
	("xOffset",   0),
	("yOffset",   0),
]

def _writeComponents(glyph, tree):
	for component in glyph.components:
		base, transformation, identifier = component
		element = ET.Element("component")
		element.attrib["base"] = base
		if transformation:
			for i, (attr, default) in enumerate(_transformationInfo):
				value = transformation[i]
				if value != default:
					element.attrib[attr] = value
		if identifier:
			element.attrib["identifier"]
		tree.append(element)

# ---------------------
# Misc Helper Functions
# ---------------------

def _relaxedSetattr(object, attr, value):
	try:
		setattr(object, attr, value)
	except AttributeError:
		pass

def _number(s):
	"""
	Given a numeric string, return an integer or a float, whichever
	the string indicates. _number("1") will return the integer 1,
	_number("1.0") will return the float 1.0.

	>>> _number("1")
	1
	>>> _number("1.0")
	1.0
	>>> _number("a")
	Traceback (most recent call last):
	    ...
	GlyphTreeError: Could not convert a to an int or float.
	"""
	try:
		n = int(s)
		return n
	except ValueError:
		pass
	try:
		n = float(s)
		return n
	except ValueError:
		raise GlyphTreeError("Could not convert %s to an int or float." % s)
