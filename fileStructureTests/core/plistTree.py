def convertTreeToPlist(tree):
	"""
	Convert an ElementTree tree/element representing
	a Property List to a nested set of Python objects.
	"""
	root = tree[0]
	return _convertElementToObj(root)

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

def _convertElementToList(element):
	obj = []
	for subElement in element:
		v = _convertElementToObj(subElement)
		obj.append(v)
	return obj

def _convertElementToInt(element):
	return int(element.text)

def _convertElementToFloat(element):
	# conform to DTD?
	return float(element.text)

def _convertElementToString(element):
	return unicode(element.text)
