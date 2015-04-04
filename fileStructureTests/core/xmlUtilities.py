"""
Miscellaneous XML tools.
"""

from xml.etree import cElementTree as ET

def treeToString(tree, header):
    indentTree(tree)
    xml = ET.tostring(tree)
    if header is not None:
        xml = header.splitlines() + [xml]
        xml = "\n".join(xml)
    return xml

def indentTree(elem, whitespace="\t", level=0):
    # taken from http://effbot.org/zone/element-lib.htm#prettyprint
    i = "\n" + level * whitespace
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + whitespace
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indentTree(elem, whitespace, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i