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
        text_decode = b64decode(NSString.text)
        # write the lyric of the slide in b64 format
        text_decode.replace(keywords, new_text)
        NSString.text = b64encode(text_decode)
    elif NSString.attrib["rvXMLIvarName"] == "RTFData":
        pass
    elif NSString.attrib["rvXMLIvarName"] == "WinFlowData":
        WinFlowData = NSString.text
    elif NSString.attrib["rvXMLIvarName"] == "WinFontData":
        WinFontData = NSString.text

    # NSString.text = ""

tree.write("output.pro6")
