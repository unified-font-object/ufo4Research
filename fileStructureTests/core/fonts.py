"""
To Do:
- do something with the specific point type counts?
- define components
"""

from copy import deepcopy
from objects import Font

profiles = """
> UFO 4-547 Glyphs
glyphs: 547
glyphs with 7 contours: 4
glyphs with 5 contours: 4
glyphs with 4 contours: 16
glyphs with 3 contours: 77
glyphs with 2 contours: 219
glyphs with 1 contours: 222
glyphs with 0 contours: 5
contours with 67 points: 2
contours with 56 points: 4
contours with 55 points: 2
contours with 53 points: 8
contours with 48 points: 1
contours with 47 points: 1
contours with 46 points: 4
contours with 45 points: 3
contours with 44 points: 1
contours with 42 points: 8
contours with 41 points: 12
contours with 40 points: 1
contours with 38 points: 4
contours with 37 points: 6
contours with 35 points: 10
contours with 34 points: 5
contours with 33 points: 3
contours with 32 points: 9
contours with 29 points: 26
contours with 28 points: 15
contours with 27 points: 19
contours with 26 points: 10
contours with 25 points: 18
contours with 24 points: 7
contours with 23 points: 21
contours with 22 points: 1
contours with 20 points: 28
contours with 19 points: 14
contours with 18 points: 9
contours with 17 points: 13
contours with 16 points: 9
contours with 15 points: 119
contours with 14 points: 32
contours with 13 points: 68
contours with 12 points: 35
contours with 11 points: 31
contours with 10 points: 19
contours with 9 points: 24
contours with 8 points: 36
contours with 7 points: 83
contours with 6 points: 20
contours with 4 points: 235
contours with 3 points: 27
moveTo points: 1003
lineTo points: 4768
curveTo points: 2815
qCurveTo points: 0
<
"""

fontInfo = {
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

def generatePoints(count, x, y):
	points = []
	for i in range(count):
		points.append((x, y))
		x += 1
		y += 1
	return points, x, y

def shuffle(stuff, recursion=0):
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
	shuffled = []
	for i in shuffler:
		shuffled += i
	if recursion < 3:
		recursion += 1
		shuffled = shuffle(shuffled, recursion)
	return shuffled

# ------------
# Pre-Compiler
# ------------

fontDescriptions = {}
currentFont = None
x = y = None
for line in profiles.splitlines():
	if line.startswith("#"):
		continue
	elif line.startswith(">"):
		x = 0
		y = 1
		name = line.split(">", 1)[1].strip()
		currentFont = dict(
			glyphs=[],
			contours=[]
		)
		fontDescriptions[name] = currentFont
	elif line.startswith("glyphs with "):
		line = line.replace("glyphs with ", "")
		line = line.replace(" contours:", "")
		contourCount, glyphCount = line.split(" ")
		glyphCount = int(glyphCount)
		contourCount = int(contourCount)
		for i in range(glyphCount):
			currentFont["glyphs"].append(contourCount)
	elif line.startswith("contours with "):
		line = line.replace("contours with ", "")
		line = line.replace(" points:", "")
		pointCount, contourCount = line.split(" ")
		contourCount = int(contourCount)
		pointCount = int(pointCount)
		for i in range(contourCount):
			contour, x, y = generatePoints(pointCount, x, y)
			currentFont["contours"].append(contour)
	elif line.startswith("<"):
		currentFont["glyphs"] = shuffle(currentFont["glyphs"])
		currentFont["contours"] = shuffle(currentFont["contours"])

# --------
# Compiler
# --------

def compileFont(name):
	description = fontDescriptions[name]
	font = Font()
	layer = font.newLayer("public.default")
	for attr, value in fontInfo.items():
		setattr(font.info, attr, value)
	contours = deepcopy(description["contours"])
	for glyphIndex, contourCount in enumerate(description["glyphs"]):
		glyph = layer.newGlyph("glyph%d" % glyphIndex)
		glyph.unicodes = [glyphIndex]
		for contourIndex in range(contourCount):
			glyph.beginPath()
			for point in contours.pop(0):
				glyph.addPoint(point, "line")
			glyph.endPath()
	return font
