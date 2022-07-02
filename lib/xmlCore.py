import json
import os
import xml.etree.ElementTree as ET

from copy import copy


def dictify(r, root=True):
    """
    Convert the xml to dict.
    """
    if root:
        return {
            r.tag: dictify(r, False)
        }
    rootTag = copy(r.attrib)
    if r.text:
        rootTag["[text]"] = r.text
    for x in r.findall("./*"):
        if x.tag not in rootTag:
            rootTag[x.tag] = []
        rootTag[x.tag].append(
            dictify(x, False)
        )
    return rootTag


def loadXml(filename):
    """
    Load the xml file.
    """
    if(not os.path.exists(filename)):
        raise Exception("The xml file does not exist.")
    with open(filename) as f:
        xmlCode = f.read()
    try:
        root = ET.fromstring(xmlCode)
        # with open("test.json", 'w') as f:
        #     json.dump(dictify(root), f, indent=4)
        return dictify(root)
    except Exception as e:
        print(e)
