import os
import shutil
import tempfile
import time
from core.ufoReaderWriter import UFOReaderWriter
from core.fonts import compileFont
from core.objects import Font

# ------------
# File Systems
# ------------

fileSystems = {}

from ufo3 import UFO3FileSystem
fileSystems["UFO 3"] = UFO3FileSystem

from singleXML import SingleXMLFileSystem
fileSystems["Single XML"] = SingleXMLFileSystem

from ufo3zip import UFO3ZipFileSystem
fileSystems["UFO 3 Zipped"] = UFO3ZipFileSystem

from sqlite import SqliteFileSystem
fileSystems["Flat SQLite DB"] = SqliteFileSystem

# ----------
# Test Fonts
# ----------

testFonts = [
	("file structure building test", "Test font only to be used when developing file structures.")
]

# --------------
# Test Functions
# --------------

tests = {}

def testFullWrite(fileSystem=None, font=None):
	"""
	Fully write a new font.
	"""
	writer = UFOReaderWriter(fileSystem)
	writer.writeMetaInfo()
	writer.writeInfo(font.info)
	writer.writeGroups(font.groups)
	writer.writeKerning(font.kerning)
	writer.writeLib(font.lib)
	writer.writeFeatures(font.features)
	for layerName, layer in font.layers.items():
		for glyph in layer:
			glyphName = glyph.name
			writer.writeGlyph(layerName, glyphName, glyph)
		writer.writeGlyphSetContents(layerName)
	writer.writeLayerContents()
	writer.close()

tests["Full Write"] = dict(
	function=testFullWrite,
	reading=False,
	writing=True
)

def testFullRead(fileSystem=None, font=None):
	"""
	Fully load an entire font.
	"""
	font = Font()
	reader = UFOReaderWriter(fileSystem)
	reader.readMetaInfo()
	reader.readInfo(font.info)
	font.groups = reader.readGroups()
	font.kerning = reader.readKerning()
	font.lib = reader.readLib()
	font.features = reader.readFeatures()
	font.loadLayers(reader)
	for layer in font.layers.values():
		for glyph in layer:
			pass
	return font

tests["Full Read"] = dict(
	function=testFullRead,
	reading=True,
	writing=False
)

# -------
# Support
# -------

def setupFile(font, fileSystem):
	writer = UFOReaderWriter(fileSystem)
	writer.writeMetaInfo()
	writer.writeInfo(font.info)
	writer.writeGroups(font.groups)
	writer.writeKerning(font.kerning)
	writer.writeLib(font.lib)
	writer.writeFeatures(font.features)
	for layerName, layer in font.layers.items():
		for glyph in layer:
			glyphName = glyph.name
			writer.writeGlyph(layerName, glyphName, glyph)
		writer.writeGlyphSetContents(layerName)
	writer.writeLayerContents()
	writer.close()

def tearDownFile(path):
	if os.path.exists(path):
		if os.path.isdir(path):
			shutil.rmtree(path)
		else:
			os.remove(path)

# -------
# Execute
# -------

def execute():
	for testName, testData in sorted(tests.items()):
		print
		print "-" * len(testName)
		print testName
		print "-" * len(testName)
		print

		for fontName, description in sorted(testFonts):
			print fontName
			print "-" * len(fontName)

			font = compileFont(fontName)

			for fileSystemName, fileSystemClass in sorted(fileSystems.items()):
				path = tempfile.mkstemp()[1]
				tearDownFile(path)
				reading = testData["reading"]
				writing = testData["writing"]
				# setup
				if reading:
					fs = fileSystemClass(path)
					setupFile(font, fs)
					del fs
				# test
				try:
					func = testData["function"]
					times = []
					for i in range(7):
						start = time.time()
						fileSystem = fileSystemClass(path)
						func(
							fileSystem=fileSystem,
							font=font
						)
						total = time.time() - start
						times.append(total)
						if not reading and writing:
							tearDownFile(path)
					times.sort()
					times = times[1:-1]
					average = sum(times) / 5.0
					print "%s:" % fileSystemName, average 
				# tear down
				finally:
					tearDownFile(path)

if __name__ == "__main__":
	execute()
