"""
This will dump an anonymous profile of a given font,
for each font (OTF-CFF, OTF-TTF formats) in a directory
and sub-directories. The profile contains hashes of
the file contents and the file name as a way of
filtering out duplicate data in the overall data set.

To Do
-----

General:
- measure font info string length
- store anchor count
- measure glyph note lengths
- count points with names/identifiers
- count smooth points
- measure glyph name lengths
- output component data
- output group data
- output feature data
- the commandline functions are clumsy
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
except ImportError:
	pass

try:
	import robofab
	haveRoboFab = True
except ImportError:
	pass

try:
	import mojo
	haveRoboFont = True
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

def profileFont(path):
	"""
	Profile a font and dump the result to stdout.
	"""
	profile = dict(
		# environment data
		outputEnvironment="Unknown",
		sourceFormat="Unknown",
		# mapping of (x, y) : count for entire font.
		# will be converted to a hash later.
		fingerprinter={},
		# number of glyphs per layer
		glyphs=[],
		# mapping of contour counts : number of glyphs with this number of contours
		contourOccurance={},
		# mapping of point count : number of contours with this point count
		pointOccurance={},
		# overall point type counts
		pointTypes=dict(
			moveTo=0,
			lineTo=0,
			curveTo=0,
			qCurveTo=0
		),
		# component transformations
		componentOccurance={},
		# kerning pairs
		kerningPairs=0,
		# groups
		groups={},
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
	profile["outputEnvironment"] = "RoboFont"
	raise NotImplementedError

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

def profileGlyph(glyph, profile):
	"""
	Profile a glyph that supports the pen protocol.
	"""
	pen = ProfilePen(profile["fingerprinter"])
	glyph.draw(pen)
	# contour counts
	contourOccurance = profile["contourOccurance"]
	contourCount = len(pen.contours)
	if contourCount not in contourOccurance:
		contourOccurance[contourCount] = 0
	contourOccurance[contourCount] += 1
	# point counts
	pointOccurance = profile["pointOccurance"]
	for contour in pen.contours:
		pointCount = contour["total"]
		if pointCount not in pointOccurance:
			pointOccurance[pointCount] = 0
		pointOccurance[pointCount] += 1
		# point types
		profile["pointTypes"]["moveTo"] += contour["moveTo"]
		profile["pointTypes"]["lineTo"] += contour["lineTo"]
		profile["pointTypes"]["curveTo"] += contour["curveTo"]
		profile["pointTypes"]["qCurveTo"] += contour["qCurveTo"]
	# component counts
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
	points (including their various types),
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
			qCurveTo=0,
			total=1
		)
		self.contours.append(d)
		self._logPoint(pt)

	def _lineTo(self, pt):
		self.contours[-1]["lineTo"] += 1
		self.contours[-1]["total"] += 1
		self._logPoint(pt)

	def _curveToOne(self, pt1, pt2, pt3):
		self.contours[-1]["curveTo"] += 1
		self.contours[-1]["total"] += 3
		self._logPoint(pt1)
		self._logPoint(pt2)
		self._logPoint(pt3)

	def _qCurveToOne(self, pt1, pt2):
		self.contours[-1]["qCurveTo"] += 1
		self.contours[-1]["total"] += 2
		self._logPoint(pt1)
		self._logPoint(pt2)

	def addComponent(self, glyphName, transformation):
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
		if not count:
			continue
		if count not in profile["groups"]:
			profile["groups"][count] = 0
		profile["groups"][count] += 1

# -----------------
# Profile: Features
# -----------------

def profileFeatures(text, profile):
	if text is not None:
		profile["features"] = len(text)

# ------------------
# Profile: Font Info
# ------------------

def profileFontInfo(info, profile):
	pass

# -----------------
# Profile to String
# -----------------

def profileToString(profile):
	lines = [
		"> %s" % profile["fingerprint"],
		"source format: %s" % profile["sourceFormat"],
		"output environment: %s" % profile["outputEnvironment"],
		"fingerprint: %s" % profile["fingerprint"],
		"layers: %d" % len(profile["glyphs"]),
		"glyphs: %d" % sum(profile["glyphs"]),
		"kerning pairs: %d" % profile["kerning"]
	]
	for contourCount, occurance in reversed(sorted(profile["contourOccurance"].items())):
		lines.append(
			"glyphs with %d contours: %d" % (contourCount, occurance)
		)
	for pointCount, occurance in reversed(sorted(profile["pointOccurance"].items())):
		lines.append(
			"contours with %d points: %d" % (pointCount, occurance)
		)
	for pointType in ("moveTo", "lineTo", "curveTo", "qCurveTo"):
		lines.append(
			"%s points: %s" % (pointType, profile["pointTypes"][pointType])
		)
	lines.append("<")
	return "\n".join(lines)

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
		if os.path.isdir(path):
			for fileName in os.listdir(path):
				if fileName.startswith("."):
					continue
				p = os.path.join(path, fileName)
				found += gatherFontPaths([p])
		else:
			if isFontPath(path):
				found.append(path)
	return found

def isFontPath(path):
	fileName = os.path.basename(path)
	suffix = os.path.splitext(fileName)[-1].lower()
	return suffix in (".otf", ".ttf", ".ufo")

# ------------
# Command Line
# ------------

usage = "%prog [options] fontpath1 fontpath2 fontdirectory"

description = """This tool dumps an anonymous profile
of the given fonts of the fonts found by
recursively searching given directories.
"""

def main():
	parser = optparse.OptionParser(usage=usage, description=description, version="%prog 0.0beta")
	(options, args) = parser.parse_args()
	paths = gatherFontPaths(args)
	dumpProfilesForFonts(paths)

if __name__ == "__main__":
	main()
