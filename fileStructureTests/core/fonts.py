import os
from copy import deepcopy
from objects import Font
from fontTools.agl import AGL2UV

aglNames = list(sorted(AGL2UV.keys()))

directory = os.path.dirname(__file__)
path = os.path.join(directory, "fontData.txt")
f = open(path, "rb")
profiles = f.read()
f.close()

shellFontInfo = {
	"ascender" : 750,
	"capHeight" : 670,
	"copyright" : "copyright",
	"descender" : -170,
	"familyName" : "Test Family",
	"note" : "This is a note.",
	"openTypeHeadLowestRecPPEM" : 9,
	"openTypeHheaAscender" : 830,
	"openTypeHheaCaretOffset" : 0,
	"openTypeHheaCaretSlopeRise" : 1,
	"openTypeHheaCaretSlopeRun" : 0,
	"openTypeHheaDescender" : -170,
	"openTypeHheaLineGap" : 0,
	"openTypeNameDesigner" : "designer",
	"openTypeNameDesignerURL" : "http://designer.url",
	"openTypeNameLicense" : "license",
	"openTypeNameLicenseURL" : "license url",
	"openTypeNameManufacturer" : "manufacturer",
	"openTypeNameManufacturerURL" : "http://manufacturer.url",
	"openTypeNameUniqueID" : "manufacturer:Test Family-Regular:2015",
	"openTypeOS2CodePageRanges" : [0, 1, 4, 7, 29],
	"openTypeOS2Panose" : [2, 13, 10, 4, 4, 5, 2, 5, 2, 3],
	"openTypeOS2Selection" : [7, 8],
	"openTypeOS2StrikeoutPosition" : 373,
	"openTypeOS2StrikeoutSize" : 151,
	"openTypeOS2SubscriptXOffset" : 41,
	"openTypeOS2SubscriptXSize" : 354,
	"openTypeOS2SubscriptYOffset" : -70,
	"openTypeOS2SubscriptYSize" : 360,
	"openTypeOS2SuperscriptXOffset" : 41,
	"openTypeOS2SuperscriptXSize" : 354,
	"openTypeOS2SuperscriptYOffset" : 380,
	"openTypeOS2SuperscriptYSize" : 360,
	"openTypeOS2Type" : [2],
	"openTypeOS2TypoAscender" : 830,
	"openTypeOS2TypoDescender" : -170,
	"openTypeOS2TypoLineGap" : 0,
	"openTypeOS2UnicodeRanges" : [0, 1, 2],
	"openTypeOS2VendorID" : "UFO4",
	"openTypeOS2WeightClass" : 800,
	"openTypeOS2WidthClass" : 5,
	"openTypeOS2WinAscent" : 956,
	"openTypeOS2WinDescent" : 262,
	"postscriptBlueFuzz" : 0,
	"postscriptBlueScale" : 0.039625,
	"postscriptBlueShift" : 7,
	"postscriptBlueValues" : [-10, 0, 544, 554, 670, 680, 750, 760],
	"postscriptFamilyBlues" : [-10, 0, 544, 554, 670, 680, 750, 760],
	"postscriptFamilyOtherBlues" : [-180, -170, 320, 330],
	"postscriptForceBold" : False,
	"postscriptOtherBlues" : [-180, -170, 320, 330],
	"postscriptStemSnapH" : [128, 145, 143],
	"postscriptStemSnapV" : [197, 202, 208, 220],
	"postscriptUnderlinePosition" : -110,
	"postscriptUnderlineThickness" : 100,
	"postscriptWeightName" : "Regular",
	"styleMapFamilyName" : "Test Family",
	"styleMapStyleName" : "regular",
	"styleName" : "Regular",
	"trademark" : "trademark",
	"unitsPerEm" : 1000,
	"versionMajor" : 1,
	"versionMinor" : 0,
	"xHeight" : 544
}

# -------
# Support
# -------

# shuffle

def shuffle(stuff, recursion=0):
	"""
	Shuffle stuff in a repeatable way.
	"""
	length = len(stuff)
	if length == 1:
		return stuff
	elif length == 2:
		return list(reversed(stuff))
	elif length < 6:
		shuffler = [
			[],
			[]
		]
	elif length < 15:
		shuffler = [
			[],
			[],
			[],
			[]
		]
	else:
		shuffler = [
			[],
			[],
			[],
			[],
			[],
			[],
			[],
			[],
			[],
			[]
		]
	i = 0
	for s in stuff:
		shuffler[i].append(s)
		i += 1
		if i == len(shuffler):
			i = 0
	del stuff[:]
	for i in shuffler:
		stuff.extend(i)
	if recursion < 3:
		recursion += 1
		shuffle(stuff, recursion)

# distribute

def distribute(stuff, targets):
	"""
	Distribute stuff to targets.
	"""
	stuff = stuff
	target = 0
	for i in stuff:
		targets[target].append(i)
		target += 1
		if target == len(targets):
			target = 0

# stuff genertors

def generateList(stuff, length):
	"""
	Generate a list from the stuff with the given length.
	"""
	result = []
	candidates = []
	for i in range(length):
		if not candidates:
			candidates = list(stuff)
		result.append(candidates.pop(0))
	return result

characters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")
shuffle(characters)

def generateString(length):
	"""
	Generate a string with length.
	"""
	compiled = generateList(characters, length)
	shuffle(compiled)
	return "".join(compiled)

def generateSegments(count, x, y, typ):
	segments = []
	for i in range(count):
		segments.append(dict(type=typ, points=[]))
		if typ == "curve":
			for i in range(2):
				segments[-1]["points"].append((x, y))
				x += 1
				y += 1
		elif typ == "qCurve":
			segments[-1]["points"].append((x, y))
			x += 1
			y += 1
		segments[-1]["points"].append((x, y))
		x += 1
		y += 1
	return segments, x, y

# ------
# Parser
# ------

fontDescriptions = {}
currentFont = None
for line in profiles.splitlines():
	if line.startswith("#") or not line:
		continue
	# start
	elif line.startswith(">"):
		name = "font %d" % (len(fontDescriptions) + 1)
		currentFont = dict(
			fontInfo=0,
			kerning=0,
			groups=0,
			groupContents=0,
			features=0,
			layers=0,
			glyphs={},
			contours={},
			components={}
		)
		fontDescriptions[name] = currentFont
	# name
	elif line.startswith("fingerprint"):
		currentFont["fingerprint"] = line.split(":", 1)[-1].strip()
	# font info
	elif line.startswith("font info characters:"):
		currentFont["fontInfo"] = int(line.split(":")[-1].strip())
	# kerning
	elif line.startswith("kerning pairs:"):
		currentFont["kerning"] = int(line.split(":")[-1].strip())
	# groups
	elif line.startswith("groups:"):
		currentFont["groups"] = int(line.split(":")[-1].strip())
	elif line.startswith("group members:"):
		currentFont["groupContents"] = int(line.split(":")[-1].strip())
	# features
	elif line.startswith("features:"):
		currentFont["features"] = int(line.split(":")[-1].strip())
	# layers
	elif line.startswith("layers:"):
		currentFont["layers"] = int(line.split(":")[-1].strip())
	# glyphs
	elif line.startswith("glyphs:"):
		currentFont["glyphCount"] = int(line.split(":")[-1].strip())
	elif line.startswith("glyphs with "):
		line = line.replace("glyphs with ", "")
		line = line.replace(" contours:", "")
		contourCount, glyphCount = line.split(" ")
		glyphCount = float(glyphCount)
		contourCount = int(contourCount)
		currentFont["glyphs"][contourCount] = glyphCount
	elif line.startswith("glyph name characters:"):
		currentFont["glyphNames"] = int(line.split(":")[-1].strip())
	elif line.startswith("glyph note characters:"):
		currentFont["glyphNotes"] = int(line.split(":")[-1].strip())
	# contours
	elif line.startswith("contours:"):
		currentFont["contourCount"] = int(line.split(":")[-1].strip())
	elif line.startswith("contours with "):
		line = line.replace("contours with ", "")
		line = line.replace(" segments:", "")
		segmentCount, contourCount = line.split(" ")
		contourCount = float(contourCount)
		segmentCount = int(segmentCount)
		currentFont["contours"][segmentCount] = contourCount
	# segments
	elif line.startswith("segments:"):
		currentFont["segments"] = int(line.split(":")[-1].strip())
	elif line.startswith("moveTo segments:"):
		currentFont["moveToSegments"] = float(line.split(":")[-1].strip())
	elif line.startswith("lineTo segments:"):
		currentFont["lineToSegments"] = float(line.split(":")[-1].strip())
	elif line.startswith("curveTo segments:"):
		currentFont["curveToSegments"] = float(line.split(":")[-1].strip())
	elif line.startswith("qCurveTo segments:"):
		currentFont["qCurveToSegments"] = float(line.split(":")[-1].strip())
	# components
	elif line.startswith("components:"):
		currentFont["componentCount"] = int(line.split(":")[-1].strip())
	elif line.startswith("components with ("):
		line = line.replace("components with (", "")
		line = line.replace(") transformation:", "")
		parts = line.split(" ")
		transformation = parts[:-1]
		glyphCount = parts[-1]
		glyphCount = float(glyphCount)
		transformation = tuple([float(i) for i in transformation])
		currentFont["components"][transformation] = glyphCount

# ------------
# Pre-Compiler
# ------------

fontInfoStringAttributes = """
familyName
styleName
styleMapFamilyName
styleMapStyleName
copyright
trademark
note
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
postscriptFontName
postscriptFullName
postscriptWeightName
macintoshFONDName
""".strip().split()

for font in fontDescriptions.values():
	# glyphs
	## segments
	totalSegments = font.pop("segments")
	moveToSegmentCount = int(round(totalSegments * font.pop("moveToSegments")))
	lineToSegmentCount = int(round(totalSegments * font.pop("lineToSegments"))) 
	curveToSegmentCount = int(round(totalSegments * font.pop("curveToSegments")))
	qCurveToSegmentCount = int(round(totalSegments * font.pop("qCurveToSegments")))
	x = y = 0
	lineToSegments, x, y = generateSegments(moveToSegmentCount + lineToSegmentCount, x, y, "line")
	curveToSegments, x, y = generateSegments(curveToSegmentCount, x, y, "curve")
	qCurveToSegments, x, y = generateSegments(qCurveToSegmentCount, x, y, "qCurve")
	segments = lineToSegments + curveToSegments + qCurveToSegments
	shuffle(segments)
	generatedTotal = moveToSegmentCount + lineToSegmentCount + curveToSegmentCount + qCurveToSegmentCount
	assert generatedTotal == totalSegments
	## contours
	totalContours = font.pop("contourCount")
	contours = []
	for segmentCount, contourCount in sorted(font.pop("contours").items()):
		contourCount = int(round(totalContours * contourCount))
		for i in range(contourCount):
			contour = segments[:segmentCount]
			segments = segments[segmentCount:]
			contours.append(contour)
	shuffle(contours)
	assert len(contours) == totalContours
	## glyph
	totalGlyphs = font.pop("glyphCount")
	width = 1
	glyphs = []
	for contourCount, glyphCount in sorted(font.pop("glyphs").items()):
		glyphCount = int(round(totalGlyphs * glyphCount))
		for i in range(glyphCount):
			glyph = dict(
				name="",
				unicode=None,
				width=width,
				contours=contours[:contourCount],
				components=[],
				note=""
			)
			glyphs.append(glyph)
			contours = contours[contourCount:]
			width += 1
	## name & unicode
	candidates = []
	loop = -1
	for i in range(len(glyphs)):
		if not candidates:
			candidates = list(aglNames)
			loop += 1
		name = candidates.pop(0)
		if loop:
			name += ".alt%d" % loop
		uni = AGL2UV.get(name)
		glyphs[i]["name"] = name
		glyphs[i]["unicode"] = uni
	glyphNames = sorted([i["name"] for i in glyphs])
	## components
	totalComponents = font.pop("componentCount")
	baseGlyphs = generateList(glyphNames, totalComponents)
	components = []
	for transformation, componentCount in sorted(font.pop("components").items()):
		componentCount = int(round(totalComponents * componentCount))
		for i in range(componentCount):
			component = (baseGlyphs.pop(0), transformation)
			components.append(component)
	assert len(components) == totalComponents
	glyphComponents = [d["components"] for d in glyphs]
	distribute(components, glyphComponents)
	## note
	glyphNotes = [[] for i in range(len(glyphs))]
	glyphNoteCharacters = list(generateString(font.pop("glyphNotes")))
	distribute(glyphNoteCharacters, glyphNotes)
	for i, note in enumerate(glyphNotes):
		glyphs[i]["note"] = "".join(note)
	# layers
	layers = {}
	for i in range(font["layers"]):
		if i == 0:
			name = "public.default"
		else:
			name = "layer%d" % i
		layers[name] = []	
	font["layers"] = layers
	layers = [v for k, v in sorted(layers.items())]
	distribute(glyphs, layers)
	# fontInfo
	fontInfo = deepcopy(shellFontInfo)
	fontInfoCharacters = list(generateString(font["fontInfo"]))
	fontInfoStrings = [[] for i in range(len(fontInfoStringAttributes))]
	distribute(fontInfoCharacters, fontInfoStrings)
	for i, key in enumerate(sorted(fontInfoStringAttributes)):
		fontInfo[key] = "".join(fontInfoStrings[i])
	font["fontInfo"] = fontInfo
	# kerning
	kerning = {}
	value = 1
	for i1, side1 in enumerate(glyphNames):
		for i2, side2 in enumerate(glyphNames):
			if len(kerning) == font["kerning"]:
				break
			if i2 % 2:
				v = -value
			else:
				v = value
			kerning[side1, side2] = v
			value += 1
	font["kerning"] = kerning
	# groups
	font["groups"] = {"group%d" % (i + 1) : [] for i in range(font["groups"])}
	groups = [v for k, v in sorted(font["groups"].items())]
	groupContents = generateList(glyphNames, font.pop("groupContents"))
	shuffle(groupContents)
	distribute(groupContents, groups)
	# features
	font["features"] = generateString(font["features"])



# --------
# Compiler
# --------

# def compileFont(name):
# 	description = fontDescriptions[name]
# 	font = Font()
# 	layer = font.newLayer("public.default")
# 	for attr, value in fontInfo.items():
# 		setattr(font.info, attr, value)
# 	contours = deepcopy(description["contours"])
# 	for glyphIndex, contourCount in enumerate(description["glyphs"]):
# 		glyph = layer.newGlyph("glyph%d" % glyphIndex)
# 		glyph.unicodes = [glyphIndex]
# 		for contourIndex in range(contourCount):
# 			glyph.beginPath()
# 			for point in contours.pop(0):
# 				glyph.addPoint(point, "line")
# 			glyph.endPath()
# 	return font
