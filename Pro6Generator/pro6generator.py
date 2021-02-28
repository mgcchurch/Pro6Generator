import xml.etree.ElementTree as ET
from base64 import b64encode
from base64 import b64decode

tree = ET.parse('template.pro6')
root = tree.getroot()

first_slide = True
for array in root.iter('array'):
    for RVDisplaySlide in array.findall('RVDisplaySlide'):
        if first_slide:
            first_slide = False
        else:
            array.remove(RVDisplaySlide)
keywords = '1234567890'
new_text = 'lyrics sample'
for NSString in root.iter('NSString'):
    if NSString.attrib["rvXMLIvarName"] == "PlainText": # find the section of plain text
        # write the lyric of the slide in b64 format
        text_decode = str(b64decode(NSString.text), encoding = "utf-8")
        text_decode = text_decode.replace(keywords, new_text)
        text_bytes = b64encode(bytes(text_decode, encoding="utf8"))
        NSString.text = str(text_bytes, encoding="utf-8")

    elif NSString.attrib["rvXMLIvarName"] == "RTFData":
        # write the lyric of the slide in b64 format
        text_decode = str(b64decode(NSString.text), encoding = "utf-8")
        text_decode = text_decode.replace(keywords, new_text)
        text_bytes = b64encode(bytes(text_decode, encoding="utf8"))
        NSString.text = str(text_bytes, encoding="utf-8")

    elif NSString.attrib["rvXMLIvarName"] == "WinFlowData":
        # write the lyric of the slide in b64 format
        text_decode = str(b64decode(NSString.text), encoding = "utf-8")
        text_decode = text_decode.replace(keywords, new_text)
        text_bytes = b64encode(bytes(text_decode, encoding="utf8"))
        NSString.text = str(text_bytes, encoding="utf-8")

    elif NSString.attrib["rvXMLIvarName"] == "WinFontData":
        WinFontData = NSString.text

tree.write("output.pro6")
