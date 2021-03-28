import xml.etree.ElementTree as ET
from base64 import b64encode
from base64 import b64decode
import copy
import uuid
import re
from pypinyin import pinyin
import zhconv
import hashlib
import random
import requests
import time
from pathlib import Path
import argparse


class Lyric:
    def __init__(self, lyrics_file):
        self.lyric = {"Title": [], "Intro": [],
                      "Verse 1": [], "Verse 2": [], "Verse 3": [], "Verse 4": [], "Verse 5": [], "Verse 6": [],
                      "Verse 7": [], "Verse 8": [], "Verse 9": [], "PreChorus": [],
                      "Chorus 1": [], "Chorus 2": [], "Chorus 3": [], "Chorus 4": [], "Chorus 5": [], "Chorus 6": [],
                      "Bridge 1": [], "Bridge 2": [], "Bridge 3": [], "Ending": []
                      }
        current_section = ""
        f = open(lyrics_file, "r", encoding='utf-8')
        title = f.readline()
        self.lyric["Title"].append(title.replace("\n", ""))
        for line in f:
            section = re.search(r"\[([\w\s]+)\]", line)

            if section is not None:
                if section.group(1) in self.lyric.keys():
                    current_section = section.group(1)
                else:
                    print("Lyrics file incorrect, " + section.string + " not found!")
            else:
                if current_section != "":
                    text = line.replace("\n", "")
                    if text != "":
                        self.lyric[current_section].append(text)
        f.close()


def translate(chinese_text):
    """
    translate Chinese into English using Baidu Translate
    :param chinese_text:
    :return:
    """
    appid = 'xxxx'  # 填写你的appid
    secretKey = 'xxxx'  # 填写你的密钥

    apiURL = 'http://api.fanyi.baidu.com/api/trans/vip/translate'  # 通用翻译API HTTP地址
    salt = str(random.randint(32768, 65536))
    # 准备计算 sign 值需要的字符串
    pre_sign = appid + chinese_text + salt + secretKey
    # 计算 md5 生成 sign
    sign = hashlib.md5(pre_sign.encode()).hexdigest()
    # 请求 apiURL 所有需要的参数
    params = {
        'q': chinese_text,
        'from': 'cht',
        'to': 'en',
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    try:
        # 直接将 params 和 apiURL 一起传入 requests.get() 函数
        response = requests.get(apiURL, params=params)
        # 获取返回的 json 数据
        result_dict = response.json()
        # 得到的结果正常则 return
        if 'trans_result' in result_dict:
            return result_dict
        else:
            print('Some errors occured:\n', result_dict)
    except Exception as e:
        print('Some errors occured: ', e)


class Pro6Generator:
    def __init__(self):
        self.init = False
        parser = argparse.ArgumentParser(description='Pro6 Generator')
        parser.add_argument('-t', '--template', type=open)
        parser.add_argument('-f', '--lyricsfile', type=open)
        parser.add_argument('-d', '--lyricsfolder')
        self.args = parser.parse_args()

        if self.args.template is None:
            print("Template file is not defined!")
            return

        if self.args.lyricsfile is not None:
            self.convert_file = True
        elif self.args.lyricsfolder is not None:
            self.convert_file = False
        else:
            print("Lyrics file or folder is not defined!")
            return

        self.tree = None
        self.root = None
        self.lyric_instance = None
        self.group_copy = None
        self.slide_copy = None
        self.group_color_dict = {"Title": "1 1 0 1", "Intro": "1 1 0 1", "Verse 1": "0 0 1 1", "Verse 2": "0 1 0.5 1",
                                 "Verse 3": "1 0.65 0 1", "Verse 4": "0 0 1 1", "Verse 5": "0 1 0.5 1",
                                 "Verse 6": "1 0.65 0 1", "Verse 7": "0 0 1 1", "Verse 8": "0 1 0.5 1",
                                 "Verse 9": "1 0.65 0 1", "PreChorus": "1 0.5 0 1",
                                 "Chorus 1": "1 0 0 1", "Chorus 2": "0.93 0.5 0.93 1", "Chorus 3": "0.67 0.67 0.67 1",
                                 "Bridge 1": "1 1 1 1", "Bridge 2": "0.6 0.4 0.2 1", "Bridge 3": "1 0.5 0 1",
                                 "Ending": "0 1 1 1"}
        self.init = True

    def import_template(self, template):
        self.tree = ET.parse(template)
        self.root = self.tree.getroot()

    def generate_pro6(self):
        if self.convert_file:
            self.process_convert(self.args.lyricsfile.name)
            self.tree.write('Lyrics_Pro6/' + self.args.lyricsfile.name.rstrip(".txt") + '.pro6', encoding="utf-8", xml_declaration=True)
        else:
            for lyrics_file in Path(self.args.lyricsfolder).iterdir():
                if lyrics_file.is_file():
                    self.process_convert(lyrics_file)
                    self.tree.write('Lyrics_Pro6/' + lyrics_file.stem + '.pro6', encoding="utf-8", xml_declaration=True)

    def process_convert(self, lyrics_file):
        slide_array = None
        group_array = None

        pro6_generator.import_template(self.args.template.name)

        self.lyric_instance = Lyric(lyrics_file)

        for slide in self.tree.findall("./array/RVSlideGrouping/array[@rvXMLIvarName='slides']"):
            slide_array = slide
        if slide_array is None:
            print("Pro6 template is incorrect!")
            return

        for RVDisplaySlide in self.tree.findall("./array/RVSlideGrouping/array/RVDisplaySlide"):
            self.slide_copy = copy.deepcopy(RVDisplaySlide)
            slide_array.remove(RVDisplaySlide)

        for array in self.tree.findall("./array[@rvXMLIvarName='groups']"):
            group_array = array
        if group_array is None:
            print("Pro6 template is incorrect!")
            return

        # find the target element RVDisplaySlide
        for RVSlideGrouping in self.tree.findall("./array/RVSlideGrouping"):
            self.group_copy = copy.deepcopy(RVSlideGrouping)
            group_array.remove(RVSlideGrouping)

        for label, section in self.lyric_instance.lyric.items():
            if not section:
                continue
            else:
                group = self.create_group(group_array, label)
                for text in section:
                    # lower the request frequency of Baidu Translate
                    time.sleep(0.5)
                    self.create_slide(group, text)

    def create_group(self, parent, label):
        """
        create group element under parent
        :param label: the label of the new group
        :param parent: create group under parent
        :return: new group
        """
        new_group = copy.deepcopy(self.group_copy)
        new_group.attrib["name"] = label
        new_group.attrib["color"] = self.group_color_dict[label]
        new_group.attrib["uuid"] = str(uuid.uuid4())
        parent.append(new_group)

        return new_group

    def create_slide(self, group, text):
        """
        create slide element under the group
        :param group: group name in which you want to create slide
        :param text: text in the slide
        :return: none
        """
        parent = None
        for slide_parent in group.findall(".array[@rvXMLIvarName='slides']"):
            parent = slide_parent

        new_slide = copy.deepcopy(self.slide_copy)
        new_slide.attrib["UUID"] = str(uuid.uuid4())

        keywords = {
            "traditional": '繁體中文',
            "simple": '简体中文',
            "english": 'English',
            "pinyin": 'Pinyin'
        }

        text_english = ""
        translate_result = translate(text)
        if translate_result is not None:
            text_english = translate_result['trans_result'][0]['dst']

        content = {
            "traditional": text,
            "simple": zhconv.convert(text, 'zh-cn'),
            "english": text_english,
            "pinyin": ' '.join([''.join(s) for s in pinyin(text)])
        }
        # update UUID in RVDisplaySlide
        new_slide.attrib["UUID"] = str(uuid.uuid4()).upper()
        # update UUID in RVTextElement
        for RVTextElement in new_slide.findall("./array/RVTextElement"):
            RVTextElement.attrib["UUID"] = str(uuid.uuid4())

            for NSString_PlainText in RVTextElement.findall("./NSString[@rvXMLIvarName='PlainText']"):
                for key in keywords:
                    if NSString_PlainText.text == str(b64encode(bytes(keywords[key], encoding="utf8")),
                                                      encoding="utf-8"):  # find the element of '繁體中文'
                        for NSString in RVTextElement.iter('NSString'):
                            if NSString.attrib["rvXMLIvarName"] == "PlainText":
                                # Replace the '繁體中文' with new text
                                text_decode = str(b64decode(NSString.text), encoding="utf-8")
                                text_decode = text_decode.replace(keywords[key], content[key])
                                text_bytes = b64encode(bytes(text_decode, encoding="utf8"))
                                NSString.text = str(text_bytes, encoding="utf-8")

                            elif NSString.attrib["rvXMLIvarName"] == "RTFData":
                                # write the lyric of the slide in b64 format
                                text_decode = str(b64decode(NSString.text), encoding="utf-8")
                                text_decode = text_decode.replace(keywords[key], content[key])
                                text_bytes = b64encode(bytes(text_decode, encoding="utf8"))
                                NSString.text = str(text_bytes, encoding="utf-8")

                            elif NSString.attrib["rvXMLIvarName"] == "WinFlowData":
                                # write the lyric of the slide in b64 format
                                text_decode = str(b64decode(NSString.text), encoding="utf-8")
                                text_decode = text_decode.replace(keywords[key], content[key])
                                text_bytes = b64encode(bytes(text_decode, encoding="utf8"))
                                NSString.text = str(text_bytes, encoding="utf-8")

        parent.append(new_slide)

        return


if __name__ == "__main__":
    """
    command 1: sbms_maintenance program program_zip_file
    command 2: sbms_maintenance upgrade upgrade_zip_file
    """
    pro6_generator = Pro6Generator()
    pro6_generator.generate_pro6()
