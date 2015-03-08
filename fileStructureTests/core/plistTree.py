from xml.etree import cElementTree as ET
from xmlUtilities import treeToString

def convertTreeToPlist(tree):
	"""
	Convert an ElementTree tree/element representing
	a Property List to a nested set of Python objects.
	"""
	root = tree[0]
	return _convertElementToObj(root)

def convertPlistToTree(obj):
	"""
	Convert a nested set of objects representing a
	Property List to an ElementTree tree/element.
	"""
	assert isinstance(obj, dict)
	tree = ET.Element("plist")
	tree.attrib["version"] = "1.0"
	element = _convertObjToElement(obj)
	tree.append(element)
	return tree

plistHeader = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
""".strip()

# -------
# Support
# -------

def _convertElementToObj(element):
	tag = element.tag
	if tag == "dict":
		return _convertElementToDict(element)
	elif tag == "array":
		return _convertElementToList(element)
	elif tag == "string":
		return _convertElementToString(element)
	elif tag == "integer":
		return _convertElementToInt(element)
	elif tag == "real":
		return _convertElementToFloat(element)
	elif tag == "false":
		return False
	elif tag == "true":
		return True
	# XXX data, date
	else:
		print tag

def _convertObjToElement(obj):
	if isinstance(obj, dict):
		return _convertDictToElement(obj)
	elif isinstance(obj, (list, tuple)):
		return _convertListToElement(obj)
	elif isinstance(obj, basestring):
		return _convertStringToElement(obj)
	elif isinstance(obj, int):
		return _convertIntToElement(obj)
	elif isinstance(obj, float):
		return _convertFloatToElement(obj)
	elif isinstance(obj, bool):
		if obj == False:
			return ET.Element("false")
		else:
			return ET.Element("true")

def _convertElementToDict(element):
	obj = {}
	currentKey = None
	for subElement in element:
		tag = subElement.tag
		if tag == "key":
			currentKey = subElement.text.strip()
		else:
			obj[currentKey] = _convertElementToObj(subElement)
			currentKey = None
	return obj

def _convertDictToElement(obj):
	element = ET.Element("dict")
	for key, value in sorted(obj.items()):
		if value is None:
			continue
		assert isinstance(key, basestring)
		subElement = ET.Element("key")
		subElement.text = key
		element.append(subElement)
		subElement = _convertObjToElement(value)
		element.append(subElement)
	return element

def _convertElementToList(element):
	obj = []
	for subElement in element:
		v = _convertElementToObj(subElement)
		obj.append(v)
	return obj

def _convertListToElement(obj):
	element = ET.Element("array")
	for v in obj:
		subElement = _convertObjToElement(v)
		element.append(subElement)
	return element

def _convertElementToInt(element):
	return int(element.text)

def _convertIntToElement(obj):
	element = ET.Element("integer")
	element.text = str(obj)
	return element

# XXX these float conversions may require truncation. see the DTD for details.
# XXX (I'm on flight right now, otherwise I would.)

def _convertElementToFloat(element):
	return float(element.text)

def _convertFloatToElement(obj):
	element = ET.Element("real")
	element.text = str(obj)
	return element

def _convertElementToString(element):
	return unicode(element.text)

def _convertStringToElement(obj):
	element = ET.Element("string")
	element.text = obj
	return element
