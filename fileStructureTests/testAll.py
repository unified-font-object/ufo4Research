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
fileSystems["UFO3"] = UFO3FileSystem

# ----------
# Test Fonts
# ----------

testFonts = [
	("simple test font", "Test font description.")
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
# Execute
# -------

def _writeSourceFile(font, fileSystem):
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
			if os.path.exists(path):
				os.remove(path)
			# setup
			if testData["reading"]:
				fs = fileSystemClass(path)
				_writeSourceFile(font, fs)
				del fs
			# test
			try:
				func = testData["function"]
				fileSystem = fileSystemClass(path)
				start = time.time()
				func(
					fileSystem=fileSystem,
					font=font
				)
				total = time.time() - start
				print "%s:" % fileSystemName, total 
			# tear down
			finally:
				if os.path.exists(path):
					if os.path.isdir(path):
						shutil.rmtree(path)
					else:
						os.remove(path)



