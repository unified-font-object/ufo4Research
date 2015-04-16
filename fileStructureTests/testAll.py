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

"""
Needed Tests
------------

- Remove glyphs.
  This will require a BaseFileSystem modification.
  Something like removeBytesFromLocation.
- Test memory usage of the file system after a full read.
  sys.getsizeof will give some info. It won't be perfect
  but it will still be useful to see the values.
- Retrieve a cmap for each layer.
"""

tests = {}

# Tests are stored as dicts:
# "test name" : {
#     function : test function,
#     reading : bool indicating if the function reads a file,
#     writing : bool indicating if the function writes a file,
#     time : bool indicating if the function should be timed (optional, default is False),
# }


def testFileSize(fileSystem=None, font=None, path=None, **kwargs):
	"""
	Test the resulting size of a written file.
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
	size = _getFileSize(path)
	size = "{:,d} bytes".format(size)
	return size

def _getFileSize(path):
	if path.startswith("."):
		return 0
	if os.path.isdir(path):
		total = 0
		for p in os.listdir(path):
			total += _getFileSize(os.path.join(path, p))
		return total
	else:
		return os.stat(path).st_size

tests["File Size"] = dict(
	function=testFileSize,
	reading=False,
	writing=True
)

def testFullWrite(fileSystem=None, font=None, **kwargs):
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
	writing=True,
	time=True
)

def testFullRead(fileSystem=None, font=None, **kwargs):
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

tests["Full Read"] = dict(
	function=testFullRead,
	reading=True,
	writing=False,
	time=True
)

def testPartialRead(fileSystem=None, font=None, **kwargs):
	"""
	Load 25% of the glyphs in the font.
	"""
	font = Font()
	reader = UFOReaderWriter(fileSystem)
	reader.readMetaInfo()
	glyphNames = []
	font.loadLayers(reader)
	for layerName, layer in font.layers.items():
		for glyphName in layer.keys():
			glyphNames.append((glyphName, layerName))
	glyphNames.sort()
	glyphCount = int(len(glyphNames) * 0.25)
	glyphNames = glyphNames[:glyphCount]
	for glyphName, layerName in glyphNames:
		layer = font.layers[layerName]
		glyph = layer[glyphName]

tests["Partial Read"] = dict(
	function=testPartialRead,
	reading=True,
	writing=False,
	time=True
)

def testPartialWrite(fileSystem=None, font=None, **kwargs):
	"""
	Write 25% of the glyphs in the font.
	"""
	font = Font()
	# initialize
	reader = UFOReaderWriter(fileSystem)
	reader.readMetaInfo()
	# modify
	glyphNames = []
	font.loadLayers(reader)
	for layerName, layer in font.layers.items():
		for glyphName in layer.keys():
			glyphNames.append((glyphName, layerName))
	glyphNames.sort()
	glyphCount = int(len(glyphNames) * 0.25)
	glyphNames = glyphNames[:glyphCount]
	for glyphName, layerName in glyphNames:
		layer = font.layers[layerName]
		glyph = layer[glyphName]
		glyph.note = "partial modify"
	# write
	writer = reader
	writer.writeMetaInfo()
	for glyphName, layerName in glyphNames:
		layer = font.layers[layerName]
		glyph = layer[glyphName]
		writer.writeGlyph(layerName, glyphName, glyph)
	for layerName in font.layers.keys():
		writer.writeGlyphSetContents(layerName)
	writer.writeLayerContents()
	writer.close()

tests["Partial Write"] = dict(
	function=testPartialWrite,
	reading=True,
	writing=False,
	time=True
)

def testDropboxWrite(fileSystem=None, font=None, **kwargs):
	"""
	Upload the output of each fileSystem to your dropbox account

	A 'dropbox.txt' with an auth token is required in the same directory.
	This file will be ignored by git.

	Required is the dropbox python API
	see https://www.dropbox.com/developers/core/docs/python

	and a auth token should be request first!
	see https://www.dropbox.com/developers/core/start/python

	result from Frederik (just in case you dont want to install everything)

	----------------------
	Upload font to dropBox
	----------------------

	file structure building test
	----------------------------
	Flat SQLite DB: 2.70396995544 (1 files)
	Single XML: 1.93647909164 (1 files)
	UFO 3: 443.017402172 (554 files)
	UFO 3 Zipped: 1.76858496666 (1 files)

	(result are very much depending on connection speed)
	"""
	dropBoxAuthTokePath = 'dropbox.txt'
	if not os.path.exists(dropBoxAuthTokePath):
		# do nothing is there is no auth token file
		return "no '%s' file, skip this test." % dropBoxAuthTokePath
	try:
		# do nothing if dropbox python api is not installed
		import dropbox
	except:
		return "dropbox python api is not installed"
	f = open(dropBoxAuthTokePath, 'r')
	dropBoxAuthToken = f.read()
	f.close()

	client = dropbox.client.DropboxClient(dropBoxAuthToken)
	try:
		client.account_info()
	except:
		# do nothing if the auth token is not valid
		return "Auth token is not valid, not able to connect."
	dropBoxRoot = "/ufoResearchTest"
	path = kwargs['path']
	root = os.path.dirname(path)
	# set a file
	setupFile(font, fileSystem)
	paths = _getAllFilesForPath(path)
	try:
		# start the time
		start = time.time()
		for fileRoot, fileName in paths:
			# set all the correct paths
			filePath = os.path.join(fileRoot, fileName)
			relativePath = os.path.relpath(filePath, root)
			dropBoxPath = os.path.join(dropBoxRoot, relativePath)
			# open the file
			f = open(filePath)
			# send the file to your dropbox client
			response = client.put_file(dropBoxPath, f)
			# close the file
			f.close()
		# get the duration
		result = "%s (%s file%s)" % (time.time() - start, len(paths), "s"[len(paths)==1:])
	except:
		# import traceback
		# print "%s: Oeps" % fileSystemName 
		# print traceback.format_exc(5)
		result = "Failed to upload to dropbox"
	return result

def _getAllFilesForPath(fontFile):
	# get files recursively if 'fontFile' is a folder 
	paths = []
	if os.path.isdir(fontFile):
		for root, dirNames, fileNames in os.walk(fontFile):
			for fileName in fileNames:
				paths.append((root, fileName))
	else:
		root = os.path.dirname(fontFile)
		fileName = os.path.basename(fontFile)
		paths = [(root, fileName)]
	return paths

tests["Dropbox Write"] = dict(
	function=testDropboxWrite,
	reading=False,
	writing=True,
	time=False
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
				path = tempfile.mkstemp(suffix=".%s" %fileSystemClass.fileExtension)[1]
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
					# timed
					if testData.get("time", False):
						times = []
						for i in range(7):
							start = time.time()
							fileSystem = fileSystemClass(path)
							func(
								fileSystem=fileSystem,
								font=font,
								path=path
							)
							total = time.time() - start
							times.append(total)
							if not reading and writing:
								tearDownFile(path)
						times.sort()
						times = times[1:-1]
						result = sum(times) / 5.0
					# other (function returns result)
					else:
						fileSystem = fileSystemClass(path)
						result = func(
							fileSystem=fileSystem,
							font=font,
							path=path
						)
						if not reading and writing:
							tearDownFile(path)
					print "%s:" % fileSystemName, result 
				# tear down
				except:
					import traceback
					print "%s: Oeps" % fileSystemName 
					print traceback.format_exc(5)
				finally:
					tearDownFile(path)

if __name__ == "__main__":
	execute()
