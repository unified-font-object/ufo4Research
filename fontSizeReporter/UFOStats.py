"""
This will dump an anonymous profile of a given font,
for each font in a directory and sub-directories.

To Do
-----

General:
- add support for KeyboardInterrupt
- build a vanilla interface for use in RoboFont and Glyphs
- write documentation

OTF:

defcon:

RoboFab:
- implement

RoboFont:
- implement

Glyphs:
- implement
"""

import md5
import os
import optparse
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

supportedFormats = set((".otf", ".ttf"))

# ---------------------
# Environment Detection
# ---------------------

haveExtractor = False
haveDefcon = False
haveRoboFab = False
haveRoboFont = False
haveGlyphsApp = False

try:
	import extractor
	haveExtractor = True
except ImportError:
	pass

try:
	import defcon
	haveDefcon = True
	supportedFormats.add(".ufo")
except ImportError:
	pass

try:
	import robofab
	haveRoboFab = True
	supportedFormats.add(".ufo")
except ImportError:
	pass

try:
	import mojo
	haveRoboFont = True
	supportedFormats.add(".ufo")
	supportedFormats.add(".vfb")
except ImportError:
	pass

# try:
# 	import ?
# 	haveGlyphsApp = True
# except ImportError:
# 	pass

# -------------
# Profile: Font
# -------------

def getFileSize(path):
	total = 0
	if os.path.isdir(path):
		for p in os.listdir(path):
			if p.startswith("."):
				continue
			p = os.path.join(path, p)
			total += getFileSize(p)
	else:
		total += os.stat(path).st_size
	return total

def profileFont(path):
	"""
	Return a profile of a font.
	"""
	profile = dict(
		# environment data
		outputEnvironment="Unknown",
		sourceFormat="Unknown",
		sourceSize=getFileSize(path),
		# mapping of (x, y) : count for entire font.
		# will be converted to a hash later.
		fingerprinter={},
		# number of glyphs per layer
		glyphs=[],
		# length of glyph notes
		glyphNotes=0,
		# total number of contours
		contours=0,
		# mapping of contour counts : number of glyphs with this number of contours
		contourOccurance={},
		# total number of segments
		segments=0,
		# mapping of segment count : number of contours with this segment count
		segmentOccurance={},
		# overall segment type counts
		segmentTypes=dict(
			moveTo=0,
			lineTo=0,
			curveTo=0,
			qCurveTo=0
		),
		# total number of components
		components=0,
		# component transformations
		componentOccurance={},
		# kerning pairs
		kerning=0,
		# groups
		groups=[],
		# characters in features
		features=0,
		# characters in all font info strings
		fontInfo=0,
	)
	# send to format specific profilers
	ext = os.path.splitext(path)[-1].lower()
	profile["sourceFormat"] = ext
	if ext in (".otf", ".ttf"):
		_profileFont_OTF(path, profile)
	elif ext == ".ufo" and (haveRoboFont or haveDefcon or haveRoboFab):
		if haveRoboFont:
			_profileFont_RoboFont(path, profile)
		elif haveDefcon:
			_profileFont_defcon(path, profile)
		elif haveRoboFab:
			_profileFont_RoboFab(path, profile)
	elif ext == ".glyphs" and haveGlyphsApp:
		_profileFont_Glyphs(path, profile)
	else:
		return
	# fingerprint
	fingerprintProfile(profile)
	# done
	return profile

def _profileFont_OTF(path, profile):
	if haveExtractor and (haveDefcon or haveRoboFab):
		if haveDefcon:
			font = defcon.Font()
		elif haveRoboFab:
			font = robofab.objects.objectsRF.RFont()
		extractor.extractUFO(path, font)
		if haveDefcon:
			_profileFont_defcon(font, profile)
		elif haveRoboFab:
			_profileFont_RoboFab(font, profile)
	else:
		profile["outputEnvironment"] = "fontTools"
		font = TTFont(path)
		glyphNames = font.getGlyphOrder()
		glyphSet = font.getGlyphSet()		
		profileGlyphSet(glyphNames, glyphSet)

def _profileFont_RoboFont(path, profile):
	"""
	RoboFont specific profiler.
	"""
	from mojo.roboFont import RFont
	font = RFont(path, showUI=False)
	# the naked() object of a RFont in RoboFont
	# is a subclass of a defcon Font object
	_profileFont_defcon(font.naked(), profile)
	profile["outputEnvironment"] = "RoboFont"

def _profileFont_Glyphs(path, profile):
	"""
	Glyphs specific profiler.
	"""
	profile["outputEnvironment"] = "Glyphs"
	raise NotImplementedError

def _profileFont_defcon(path, profile):
	"""
	defcon specific profiler.
	"""
	profile["outputEnvironment"] = "defcon"
	if isinstance(path, defcon.Font):
		font = path
	else:
		font = defcon.Font(path)
	try:
		for layer in font.layers:
			profileGlyphSet(layer.keys(), layer, profile)
	except AttributeError:
		profileGlyphSet(font.keys(), font, profile)
	profileKerning(font.kerning, profile)
	profileGroups(font.groups, profile)
	profileFeatures(font.features.text, profile)
	profileFontInfo(font.info, profile)

def _profileFont_RoboFab(path, profile):
	"""
	RoboFab specific profiler.
	"""
	profile["outputEnvironment"] = "RoboFab"
	raise NotImplementedError

# ---------------
# Profile: Glyphs
# ---------------

def profileGlyphSet(glyphNames, glyphSet, profile):
	"""
	Profile all glyphs in a glyph set.
	"""
	profile["glyphs"].append(len(glyphNames))
	for glyphName in glyphNames:
		glyph = glyphSet[glyphName]
		profileGlyph(glyph, profile)
		if hasattr(glyph, "note"):
			note = glyph.note
			if isinstance(note, basestring):
				profile["glyphNotes"] += len(note)

def profileGlyph(glyph, profile):
	"""
	Profile a glyph that supports the pen protocol.
	"""
	pen = ProfilePen(profile["fingerprinter"])
	glyph.draw(pen)
	# contour counts
	contourCount = len(pen.contours)
	profile["contours"] += contourCount
	contourOccurance = profile["contourOccurance"]
	if contourCount not in contourOccurance:
		contourOccurance[contourCount] = 0
	contourOccurance[contourCount] += 1
	# segment counts
	segmentOccurance = profile["segmentOccurance"]
	for contour in pen.contours:
		segmentCount = contour["moveTo"] + contour["lineTo"] + contour["curveTo"] + contour["qCurveTo"]
		profile["segments"] += segmentCount
		if segmentCount not in segmentOccurance:
			segmentOccurance[segmentCount] = 0
		segmentOccurance[segmentCount] += 1
		# segment types
		profile["segmentTypes"]["moveTo"] += contour["moveTo"]
		profile["segmentTypes"]["lineTo"] += contour["lineTo"]
		profile["segmentTypes"]["curveTo"] += contour["curveTo"]
		profile["segmentTypes"]["qCurveTo"] += contour["qCurveTo"]
	# component counts
	profile["components"] += len(pen.components)
	for transformation in pen.components:
		if transformation not in profile["componentOccurance"]:
			profile["componentOccurance"][transformation] = 0
		profile["componentOccurance"][transformation] += 1

def fingerprintProfile(profile):
	"""
	Generate a unique hash for the font contents.
	"""
	hashable = []
	for (x, y), count in sorted(profile["fingerprinter"].items()):
		line = "%.1f %.1f %d" % (x, y, count)
		hashable.append(line)
	hashable = "\n".join(hashable)
	m = md5.md5()
	m.update(hashable)
	profile["fingerprint"] = m.hexdigest()
	del profile["fingerprinter"]


class ProfilePen(BasePen):

	"""
	This will record the number of contours,
	segments (including their various types),
	and contours. It will simultaneously store
	all point locations for full font fingerprinting.
	"""

	def __init__(self, fingerprinter):
		self.contours = []
		self.components = []
		self._fingerprinter = fingerprinter

	def _logPoint(self, pt):
		if pt not in self._fingerprinter:
			self._fingerprinter[pt] = 0
		self._fingerprinter[pt] += 1

	def _moveTo(self, pt):
		d = dict(
			moveTo=1,
			lineTo=0,
			curveTo=0,
			qCurveTo=0
		)
		self.contours.append(d)
		self._logPoint(pt)

	def _lineTo(self, pt):
		self.contours[-1]["lineTo"] += 1
		self._logPoint(pt)

	def _curveToOne(self, pt1, pt2, pt3):
		self.contours[-1]["curveTo"] += 1
		self._logPoint(pt1)
		self._logPoint(pt2)
		self._logPoint(pt3)

	def _qCurveToOne(self, pt1, pt2):
		self.contours[-1]["qCurveTo"] += 1
		self._logPoint(pt1)
		self._logPoint(pt2)

	def addComponent(self, glyphName, transformation):
		transformation = " ".join(_numberToString(i) for i in transformation)
		self.components.append(transformation)

# ----------------
# Profile: Kerning
# ----------------

def profileKerning(kerning, profile):
	profile["kerning"] = len(kerning)

# ---------------
# Profile: Groups
# ---------------

def profileGroups(groups, profile):
	for group in groups.values():
		count = len(group)
		profile["groups"].append(count)

# -----------------
# Profile: Features
# -----------------

def profileFeatures(text, profile):
	if text is not None:
		profile["features"] = len(text)

# ------------------
# Profile: Font Info
# ------------------

fontInfoStringAttributes = """
familyName
styleName
styleMapFamilyName
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

def profileFontInfo(info, profile):
	for attr in fontInfoStringAttributes:
		if hasattr(info, attr):
			value = getattr(info, attr)
			if isinstance(value, basestring):
				profile["fontInfo"] += len(value)

# -----------------
# Profile to String
# -----------------

def profileToString(profile):
	"""
	> start of profile
	source format: source file extension
	source size: source file size in bytes
	output environment: library/app used to output the profile
	fingerprint: hash of all points in the font
	font info characters: total number of characters used in string fields in the font info
	kerning pairs: total number of kerning pairs
	groups: total number of groups
	group members: sum of the length of all groups
	feature characters: number of characters in the features
	layers: number of layers
	glyphs: number of glyphs
	glyph name characters: total number of characters used in glyph names
	glyph note characters: total number of characters used in glyph notes
	contours: total number of contours
	segments: total number of segments
	components: total number of contours
	glyphs with (number) contours: percentage of glyphs with a particular number of contours
	contours with (number) segments: percentage of contours with a particular number of segments
	(segment type) segments: percentage of segments of a particular type
	components with (transformation) transformation: percentage of components with a particular transformation
	< end of profile
	"""
	lines = [
		">",
		"source format: %s" % profile["sourceFormat"],
		"source size: %d" % profile["sourceSize"],
		"output environment: %s" % profile["outputEnvironment"],
		"fingerprint: %s" % profile["fingerprint"],
		"font info characters: %d" % profile["fontInfo"],
		"kerning pairs: %d" % profile["kerning"],
		"groups: %d" % len(profile["groups"]),
		"group members: %d" % sum(profile["groups"]),
		"feature characters: %d" % profile["features"],
		"layers: %d" % len(profile["glyphs"]),
		"glyphs: %d" % sum(profile["glyphs"]),
		"glyph note characters: %d" % profile["glyphNotes"],
		"contours: %d" % profile["contours"],
		"components: %d" % profile["components"],
		"segments: %d" % profile["segments"],
	]
	segmentCount = float(profile["segments"])
	for segmentType in ("moveTo", "lineTo", "curveTo", "qCurveTo"):
		occurance = profile["segmentTypes"][segmentType]
		occurance = occurance / segmentCount
		lines.append(
			"%s segments: %s" % (segmentType, occurance)
		)
	glyphCount = float(sum(profile["glyphs"]))
	for contourCount, occurance in reversed(sorted(profile["contourOccurance"].items())):
		occurance = occurance / glyphCount
		lines.append(
			"glyphs with %d contours: %.10f" % (contourCount, occurance)
		)
	contourCount = float(profile["contours"])
	for segmentCount, occurance in reversed(sorted(profile["segmentOccurance"].items())):
		occurance = occurance / contourCount
		lines.append(
			"contours with %d segments: %.10f" % (segmentCount, occurance)
		)
	componentCount = float(profile["components"])
	for transformation, occurance in sorted(profile["componentOccurance"].items()):
		occurance = occurance / componentCount
		lines.append(
			"components with (%s) transformation: %d" % (transformation, occurance)
		)
	lines.append("<")
	return "\n".join(lines)

def _numberToString(n):
	if int(n) == n:
		return str(int(n))
	else:
		return "%.2f" % n

# ----
# Main
# ----

def dumpProfilesForFonts(paths):
	for path in paths:
		profile = profileFont(path)
		print profileToString(profile)

def gatherFontPaths(paths):
	found = []
	for path in paths:
		if isFontPath(path):
			found.append(path)
		elif os.path.isdir(path):
			for fileName in os.listdir(path):
				if fileName.startswith("."):
					continue
				p = os.path.join(path, fileName)
				found += gatherFontPaths([p])
	return found

def isFontPath(path):
	fileName = os.path.basename(path)
	suffix = os.path.splitext(fileName)[-1].lower()
	return suffix in supportedFormats

# ------------
# Command Line
# ------------

usage = "%prog [options] fontpath1 fontpath2 fontdirectory"

description = """
This tool dumps an anonymous profile
of the given fonts of the fonts found by
recursively searching given directories.
""".strip()

def main():
	parser = optparse.OptionParser(usage=usage, description=description, version="%prog 0.0beta")
	(options, args) = parser.parse_args()
	paths = gatherFontPaths(args)
	dumpProfilesForFonts(paths)

if __name__ == "__main__":
	main()
