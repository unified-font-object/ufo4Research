from plistTree import convertTreeToPlist

class GlyphTreeError(Exception): pass

# -------------
# Glyph Reading
# -------------

def readGlyphFromTree(tree, glyphObject=None, pointPen=None, formatVersions=(1, 2)):
	formatVersion = tree.attrib.get("format", "undefined")
	try:
		v = int(formatVersion)
		formatVersion = v
	except ValueError:
		pass
	if formatVersion == 1:
		readGlyphFromTreeFormat1(tree=tree, glyphObject=glyphObject, pointPen=pointPen)
	elif formatVersion == 2:
		readGlyphFromTreeFormat2(tree=tree, glyphObject=glyphObject, pointPen=pointPen)
	else:
		raise GlyphTreeError("Unsupported GLIF format version: %s" % formatVersion)

def readGlyphFromTreeFormat1(tree, glyphObject=None, pointPen=None):
	# get the name
	_readName(glyphObject, tree)
	# populate the sub elements
	unicodes = []
	haveSeenAdvance = haveSeenOutline = haveSeenLib = haveSeenNote = False
	for element in tree:
		tag = element.tag
		if tag == "outline":
			if haveSeenOutline:
				raise GlyphTreeError("The outline element occurs more than once.")
			if attrs:
				raise GlyphTreeError("The outline element contains unknown attributes.")
			haveSeenOutline = True
			if pointPen is not None:
				buildOutlineFormat1(glyphObject, pointPen, element)
		elif glyphObject is None:
			continue
		elif tag == "advance":
			if haveSeenAdvance:
				raise GlyphTreeError("The advance element occurs more than once.")
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
		elif tag == "note":
			if haveSeenNote:
				raise GlyphTreeError("The note element occurs more than once.")
			haveSeenNote = True
			_readNote(glyphObject, element)
		elif tag == "lib":
			if haveSeenLib:
				raise GlyphTreeError("The lib element occurs more than once.")
			haveSeenLib = True
			_readLib(glyphObject, element)
		else:
			raise GlyphTreeError("Unknown element in GLIF: %s" % tag)
	# set the collected unicodes
	if unicodes:
		_relaxedSetattr(glyphObject, "unicodes", unicodes)

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
			if haveSeenOutline:
				raise GlyphTreeError("The outline element occurs more than once.")
			if attrib:
				raise GlyphTreeError("The outline element contains unknown attributes.")
			haveSeenOutline = True
			if pointPen is not None:
				buildOutlineFormat2(glyphObject, pointPen, element, identifiers)
		elif glyphObject is None:
			continue
		elif tag == "advance":
			if haveSeenAdvance:
				raise GlyphTreeError("The advance element occurs more than once.")
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
			if len(element):
				raise GlyphTreeError("Unknown children in guideline element.")
			attrib = element.attrib
			for attr in ("x", "y", "angle"):
				if attr in attrib:
					attrib[attr] = _number(attrib[attr])
			guidelines.append(attrib)
		elif tag == "anchor":
			if len(element):
				raise GlyphTreeError("Unknown children in anchor element.")
			attrib = element.attrib
			for attr in ("x", "y"):
				if attr in attrib:
					attrib[attr] = _number(attrib[attr])
			anchors.append(attrib)
		elif tag == "image":
			if haveSeenImage:
				raise GlyphTreeError("The image element occurs more than once.")
			if len(children):
				raise GlyphTreeError("Unknown children in image element.")
			haveSeenImage = True
			_readImage(glyphObject, element)
		elif tag == "note":
			if haveSeenNote:
				raise GlyphTreeError("The note element occurs more than once.")
			haveSeenNote = True
			_readNote(glyphObject, element)
		elif tag == "lib":
			if haveSeenLib:
				raise GlyphTreeError("The lib element occurs more than once.")
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
	if glyphName is None or len(glyphName) == 0:
		raise GlyphTreeError("Empty glyph name in GLIF.")
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
		return
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

contourAttributesFormat2 = set(["identifier"])
componentAttributesFormat1 = set(["base", "xScale", "xyScale", "yxScale", "yScale", "xOffset", "yOffset"])
componentAttributesFormat2 = componentAttributesFormat1 | set(["identifier"])
pointAttributesFormat1 = set(["x", "y", "type", "smooth", "name"])
pointAttributesFormat2 = pointAttributesFormat1 | set(["identifier"])
pointSmoothOptions = set(("no", "yes"))
pointTypeOptions = set(["move", "line", "offcurve", "curve", "qcurve"])

# format 1

componentAttributesFormat1 = set(["base", "xScale", "xyScale", "yxScale", "yScale", "xOffset", "yOffset"])
pointAttributesFormat1 = set(["x", "y", "type", "smooth", "name"])
pointSmoothOptions = set(("no", "yes"))
pointTypeOptions = set(["move", "line", "offcurve", "curve", "qcurve"])

def buildOutlineFormat1(glyphObject, pen, tree):
	anchors = []
	for element in tree:
		tag = element.tag
		if tag == "contour":
			if len(element) == 1:
				# XXX need to validate here
				sub = element[0]
				if sub.tag == "point":
					anchor = _buildAnchorFormat1(sub)
					if anchor is not None:
						anchors.append(anchor)
						continue
			_buildOutlineContourFormat1(pen, element)
		elif element == "component":
			_buildOutlineComponentFormat1(pen, element)
		else:
			raise GlyphTreeError("Unknown element in outline element: %s" % element)
	if glyphObject is not None and anchors:
		_relaxedSetattr(glyphObject, "anchors", anchors)

def _buildAnchorFormat1(tree):
	attrib = tree.attrib
	if attrib.get("type") != "move":
		return None
	x = attrib.get("x")
	y = attrib.get("y")
	if x is None:
		raise GlyphTreeError("Required x attribute is missing in point element.")
	if y is None:
		raise GlyphTreeError("Required y attribute is missing in point element.")
	x = _number(x)
	y = _number(y)
	name = attrib.get("name")
	anchor = dict(x=x, y=y, name=name)
	return anchor

def _buildOutlineContourFormat1(pen, tree):
	if set(tree.attrib.keys()):
		raise GlyphTreeError("Unknown attributes in contour element.")
	pen.beginPath()
	for element in tree:
		points = _validateAndMassagePointStructures(element, pointAttributesFormat1, openContourOffCurveLeniency=True)
		_buildOutlinePointsFormat1(pen, children)
	pen.endPath()

def _buildOutlinePointsFormat1(pen, tree):
	for element in tree:
		attrib = element.attrib
		x = attrib["x"]
		y = attrib["y"]
		segmentType = attrib["segmentType"]
		smooth = attrib["smooth"]
		name = attrib["name"]
		pen.addPoint((x, y), segmentType=segmentType, smooth=smooth, name=name)

def _buildOutlineComponentFormat1(pen, element):
	if len(element):
		raise GlyphTreeError("Unknown child elements of component element.")
	attrib = element.attrib
	if set(attrib.keys()) - componentAttributesFormat1:
		raise GlyphTreeError("Unknown attributes in component element.")
	baseGlyphName = attrib.get("base")
	if baseGlyphName is None:
		raise GlyphTreeError("The base attribute is not defined in the component.")
	transformation = []
	for attr, default in _transformationInfo:
		value = attrib.get(attr)
		if value is None:
			value = default
		else:
			value = _number(value)
		transformation.append(value)
	pen.addComponent(baseGlyphName, tuple(transformation))

# format 2

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
	if set(attrib.keys()) - contourAttributesFormat2:
		raise GlyphTreeError("Unknown attributes in contour element.")
	identifier = attrib.get("identifier")
	if identifier is not None:
		identifiers.add(identifier)
	try:
		pen.beginPath(identifier=identifier)
	except TypeError:
		pen.beginPath()
		raise warn("The beginPath method needs an identifier kwarg. The contour's identifier value has been discarded.", DeprecationWarning)
	for element in tree:
		element = _validateAndMassagePointStructures(element, pointAttributesFormat2)
		_buildOutlinePointsFormat2(pen, element, identifiers)
	pen.endPath()

def _buildOutlinePointsFormat2(pen, tree, identifiers):
	for element in tree:
		attrib = element.attrib
		x = attrib["x"]
		y = attrib["y"]
		segmentType = attrib["segmentType"]
		smooth = attrib["smooth"]
		name = attrib["name"]
		identifier = attrib.get("identifier")
		try:
			pen.addPoint((x, y), segmentType=segmentType, smooth=smooth, name=name, identifier=identifier)
		except TypeError:
			pen.addPoint((x, y), segmentType=segmentType, smooth=smooth, name=name)
			raise warn("The addPoint method needs an identifier kwarg. The point's identifier value has been discarded.", DeprecationWarning)

def _buildOutlineComponentFormat2(pen, element, identifiers):
	if len(element):
		raise GlyphTreeError("Unknown child elements of component element.")
	attrib = element.attrib
	if set(attrib.keys()) - componentAttributesFormat2:
		raise GlyphTreeError("Unknown attributes in component element.")
	baseGlyphName = attrib.get("base")
	if baseGlyphName is None:
		raise GlyphTreeError("The base attribute is not defined in the component.")
	transformation = []
	for attr, default in _transformationInfo:
		value = attrib.get(attr)
		if value is None:
			value = default
		else:
			value = _number(value)
		transformation.append(value)
	identifier = attrib.get("identifier")
	try:
		pen.addComponent(baseGlyphName, tuple(transformation), identifier=identifier)
	except TypeError:
		pen.addComponent(baseGlyphName, tuple(transformation))
		raise warn("The addComponent method needs an identifier kwarg. The component's identifier value has been discarded.", DeprecationWarning)

# all formats

def _validateAndMassagePointStructures(tree, pointAttributes, openContourOffCurveLeniency=False):
	if not len(tree):
		return tree
	# store some data for later validation
	pointTypes = []
	haveOnCurvePoint = False
	haveOffCurvePoint = False
	# validate and massage the individual point elements
	for element in tree:
		# not <point>
		if element.tag != "point":
			raise GlyphTreeError("Unknown child element (%s) of contour element." % subElement)
		# unknown attributes
		attrib = element.attrib
		unknownAttributes = [attr for attr in attrib.keys() if attr not in pointAttributes]
		if unknownAttributes:
			raise GlyphTreeError("Unknown attributes in point element.")
		# search for unknown children
		if len(element):
			raise GlyphTreeError("Unknown child elements in point element.")
		# x and y are required
		x = attrib.get("x")
		y = attrib.get("y")
		if x is None:
			raise GlyphTreeError("Required x attribute is missing in point element.")
		if y is None:
			raise GlyphTreeError("Required y attribute is missing in point element.")
		x = attrib["x"] = _number(x)
		y = attrib["y"] = _number(y)
		# segment type
		pointType = attrib.pop("type", "offcurve")
		if pointType not in pointTypeOptions:
			raise GlyphTreeError("Unknown point type: %s" % pointType)
		if pointType == "offcurve":
			pointType = None
		attrib["segmentType"] = pointType
		if pointType is None:
			haveOffCurvePoint = True
		else:
			haveOnCurvePoint = True
		pointTypes.append(pointType)
		# move can only occur as the first point
		if pointType == "move" and index != 0:
			raise GlyphTreeError("A move point occurs after the first point in the contour.")
		# smooth is optional
		smooth = attrib.get("smooth", "no")
		if smooth is not None:
			if smooth not in pointSmoothOptions:
				raise GlyphTreeError("Unknown point smooth value: %s" % smooth)
		smooth = smooth == "yes"
		attrib["smooth"] = smooth
		# smooth can only be applied to curve and qcurve
		if smooth and pointType is None:
			raise GlyphTreeError("smooth attribute set in an offcurve point.")
		# name is optional
		if "name" not in attrib:
			attrib["name"] = None
	if openContourOffCurveLeniency:
		# remove offcurves that precede a move. this is technically illegal,
		# but we let it slide because there are fonts out there in the wild like this.
		if tree[0].attrib["segmentType"] == "move":
			remove = []
			while 1:
				for point in reversed(tree):
					if point.attrib["segmentType"] is not None:
						break
					elif point.attrib["segmentType"] is None:
						remove.append(point)
				break
			for point in remove:
				tree.remove(point)
	# validate the off-curves in the segments
	if haveOffCurvePoint and haveOnCurvePoint:
		while pointTypes[-1] is None:
			pointTypes.insert(0, pointTypes.pop(-1))
		segment = []
		for pointType in pointTypes:
			if pointType is None:
				segment.append(pointType)
				continue
			segment.append(pointType)
			if len(segment) > 1:
				segmentType = segment[-1]
				offCurves = segment[:-1]
				# move and line can't be preceded by off-curves
				if segmentType == "move":
					# this will have been filtered out already
					raise GlyphTreeError("move can not have an offcurve.")
				elif segmentType == "line":
					raise GlyphTreeError("line can not have an offcurve.")
				elif segmentType == "curve":
					if len(offCurves) > 2:
						raise GlyphTreeError("Too many offcurves defined for curve.")
				elif segmentType == "qcurve":
					pass
				else:
					# unknown segement type. it'll be caught later.
					pass
			# reset
			segment = []
	return tree


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
