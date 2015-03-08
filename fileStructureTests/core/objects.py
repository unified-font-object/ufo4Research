class Font(object):

	def __init__(self):
		self.info = FontInfo()
		self.groups = {}
		self.kerning = {}
		self.lib = {}
		self.features = None
		self.layers = {}

	def newLayer(self, layerName):
		layer = Layer(None, layerName)
		self.layers[layerName] = layer
		return layer

	def loadLayers(self, reader):
		for layerName in reader.getLayerNames():
			self.layers[layerName] = Layer(reader, layerName)


class FontInfo(object): pass


class Layer(object):

	def __init__(self, reader, name):
		self.reader = reader
		self.name = name
		if reader is None:
			self._glyphs = {}
		else:
			self._glyphs = dict.fromkeys(reader.getGlyphNames(name))

	def newGlyph(self, glyphName):
		glyph = Glyph()
		glyph.name = glyphName
		self._glyphs[glyphName] = glyph
		return glyph

	def loadGlyph(self, glyphName):
		glyph = Glyph()
		self.reader.readGlyph(self.name, glyphName, glyph)
		return glyph

	def keys(self):
		return self._glyphs.keys()

	def __iter__(self):
		names = self.keys()
		while names:
			name = names[0]
			yield self[name]
			names = names[1:]

	def __getitem__(self, name):
		if self._glyphs[name] is None:
			self._glyphs[name] = self.loadGlyph(name)
		return self._glyphs[name]


class Glyph(object):

	def __init__(self):
		self.contours = []
		self.components = []

	def drawPoints(self, pointPen):
		raise NotImplementedError

	# -------------
	# Point Pen API
	# -------------

	def beginPath(self, identifier=None, **kwargs):
		contour = Contour()
		contour.identifier = identifier
		self.contours.append(contour)

	def endPath(self):
		pass

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, identifier=None, **kwargs):
		self.contours[-1].append((pt, segmentType, smooth, name, identifier))

	def addComponent(self, baseGlyphName, transformation, identifier=None, **kwargs):
		component = (baseGlyphName, transformation, identifier)
		self.components.append(component)


class Contour(list): pass
