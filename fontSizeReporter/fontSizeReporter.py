"""
This will dump an anonymous profile of a given font,
for each font (OTF-CFF, OTF-TTF formats) in a directory
and sub-directories. The profile contains hashes of
the file contents and the file name as a way of
filtering out duplicate data in the overall data set.

To Do:
- rather than hash the file contents and file name,
  find some way to hash the glyph outlines. this will
  make it so that UFOs and OTFs of the same data only
  count as one instance.
- if defcon is installed, read UFOs with that.
- if extractor is installed, use it to pull kerning from binaries.
- should component transformations be extracted?
- should anchors be extracted?
- extract kerning pairs and kerning groups when possible.
- in UFOs, sniff the layer glyph counts from the RoboFont lib location?
- in UFOs, measure the number of characters in the features.
- in UFOs, count the number of points with identifiers.
- count the number of smooth curve points.
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
	data = dict(
		fileName=None,
		fileContents=None,
		glyphs=0,
		contourOccurance={},
		pointOccurance={},
		componentOccurance=0,
		pointTypes=dict(
			moveTo=0,
			lineTo=0,
			curveTo=0,
			qCurveTo=0
		),
		kerningPairs=0,
		kerningGroups=0
	)
	contourOccurance = data["contourOccurance"]
	pointOccurance = data["pointOccurance"]
	# file name
	data["fileName"] = makeHash(os.path.basename(path).lower())
	# file contents
	f = open(path, "rb")
	d = f.read()
	f.close()
	data["fileContents"] = makeHash(d)
	# counting
	font = TTFont(path)
	glyphOrder = font.getGlyphOrder()
	glyphSet = font.getGlyphSet()
	for glyphName in glyphOrder:
		glyph = glyphSet[glyphName]
		pen = CounterPen()
		glyph.draw(pen)
		# contour counts
		contourCount = len(pen.contours)
		if contourCount not in contourOccurance:
			contourOccurance[contourCount] = 0
		contourOccurance[contourCount] += 1
		# point counts
		for contour in pen.contours:
			pointCount = contour["total"]
			if pointCount not in pointOccurance:
				pointOccurance[pointCount] = 0
			pointOccurance[pointCount] += 1
			# point types
			data["pointTypes"]["moveTo"] += contour["moveTo"]
			data["pointTypes"]["lineTo"] += contour["lineTo"]
			data["pointTypes"]["curveTo"] += contour["curveTo"]
			data["pointTypes"]["qCurveTo"] += contour["qCurveTo"]
		# component counts
		data["componentOccurance"] += pen.components
	data["glyphs"] = len(glyphOrder)
	# dump
	print "> %d Glyphs (%s)" % (data["glyphs"], data["fileName"])
	print "file name:", data["fileName"]
	print "file contents:", data["fileContents"]
	print "glyphs:", data["glyphs"]
	for contourCount, occurance in reversed(sorted(data["contourOccurance"].items())):
		print "glyphs with %d contours:" % contourCount, occurance
	for pointCount, occurance in reversed(sorted(data["pointOccurance"].items())):
		print "contours with %d points:" % pointCount, occurance
	for pointType in ("moveTo", "lineTo", "curveTo", "qCurveTo"):
		print "%s points:" % pointType, data["pointTypes"][pointType]
	print "<"

def makeHash(data):
	m = md5.md5()
	m.update(data)
	return m.hexdigest()


class CounterPen(BasePen):

	def __init__(self):
		self.contours = []
		self.components = 0

	def _moveTo(self, pt):
		d = dict(
			moveTo=1,
			lineTo=0,
			curveTo=0,
			qCurveTo=0,
			total=1
		)
		self.contours.append(d)

	def _lineTo(self, pt):
		self.contours[-1]["lineTo"] += 1
		self.contours[-1]["total"] += 1

	def _curveToOne(self, pt1, pt2, pt3):
		self.contours[-1]["curveTo"] += 1
		self.contours[-1]["total"] += 3

	def _qCurveToOne(self, pt1, pt2):
		self.contours[-1]["qCurveTo"] += 1
		self.contours[-1]["total"] += 2

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
