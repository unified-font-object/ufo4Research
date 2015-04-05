"""
This will dump an anonymous profile of a given font,
for each font (OTF-CFF, OTF-TTF formats) in a directory
and sub-directories. The profile contains hashes of
the file contents and the file name as a way of
filtering out duplicate data in the overall data set.

To Do:
- if defcon is installed, read UFOs with that.
- if extractor is installed, use it to pull kerning from binaries.
- should component transformations be extracted?
- should anchors be extracted?
- extract kerning pairs and kerning groups when possible.
- in UFOs, sniff the layer glyph counts from the RoboFont lib location?
- in UFOs, measure the number of characters in the features.
- in UFOs, count the number of points with identifiers.
- count the number of smooth curve points.
- measure string lengths in font info and note them as an overall total.
  this can then be split or stored in a single field in the generated UFOs.
- should glyph name lengths be measured?
- should point identifiers be assigned? these can potentially be a lot of data.
- measure feature string length.
- lib should be ignored.
- measure glyph note lengths and store that as a single value.
"""

import md5
import os
import optparse
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

# ----
# Main
# ----

def dumpProfilesForFonts(paths):
	for path in paths:
		profileFont(path)

# --------------
# File Gathering
# --------------

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
	return suffix in (".otf", ".ttf")

# --------
# Profiler
# --------

def profileFont(path):
	"""
	Profile a font and dump the result to stdout.
	"""
	profile = dict(
		fingerprinter={},
		glyphs=0,
		contourOccurance={},
		pointOccurance={},
		componentOccurance=0,
		pointTypes=dict(
			moveTo=0,
			lineTo=0,
			curveTo=0,
			qCurveTo=0
		)
	)
	# counting
	font = TTFont(path)
	glyphOrder = font.getGlyphOrder()
	glyphSet = font.getGlyphSet()
	for glyphName in glyphOrder:
		glyph = glyphSet[glyphName]
		profileGlyph(glyph, profile)
	profile["glyphs"] = len(glyphOrder)
	fingerprintProfile(profile)
	# dump
	print "> %d Glyphs (%s)" % (profile["glyphs"], profile["fingerprint"])
	print "fingerprint:", profile["fingerprint"]
	print "glyphs:", profile["glyphs"]
	for contourCount, occurance in reversed(sorted(profile["contourOccurance"].items())):
		print "glyphs with %d contours:" % contourCount, occurance
	for pointCount, occurance in reversed(sorted(profile["pointOccurance"].items())):
		print "contours with %d points:" % pointCount, occurance
	for pointType in ("moveTo", "lineTo", "curveTo", "qCurveTo"):
		print "%s points:" % pointType, profile["pointTypes"][pointType]
	print "<"

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
	profile["componentOccurance"] += pen.components

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
		self.components = 0
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
		self.components += 1

# --------------------
# Command Line Behvior
# --------------------

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
