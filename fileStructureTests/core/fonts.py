"""
To Do:
- do something with the specific point type counts.
- define components
- build objects for any other data that the data defines.
"""

import os
from copy import deepcopy
from objects import Font

directory = os.path.dirname(__file__)
path = os.path.join(directory, "fontData.txt")
f = open(path, "rb")
profiles = f.read()
f.close()

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
