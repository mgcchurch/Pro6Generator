import xml.etree.ElementTree as ET
from base64 import b64encode
from base64 import b64decode
import copy
import uuid
from lyricsmaster import LyricWiki, TorController
import re
from pypinyin import pinyin


class Lyric:
    def __init__(self, lyrics_file):
        self.lyric = {"Intro": [], "Verse 1": [], "Verse 2": [], "Verse 3": [], "PreChorus": [],
                      "Chorus 1": [], "Chorus 2": [], "Chorus 3": [],
                      "Bridge 1": [], "Bridge 2": [], "Bridge 3": [],
                      "Ending": []}
        current_section = ""
        f = open(lyrics_file, "r", encoding='utf-8')
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


class Pro6Generator:
    def __init__(self):
        self.tree = None
        self.root = None
        self.lyric_instance = Lyric('lyrics.txt')
        self.group_copy = None
        self.slide_copy = None
        self.group_color_dict = {"Intro": "1 1 0 1", "Verse 1": "0 0 1 1", "Verse 2": "0 1 0.5 1",
                                 "Verse 3": "1 0.65 0 1", "PreChorus": "1 0.5 0 1",
                                 "Chorus 1": "1 0 0 1", "Chorus 2": "0.93 0.5 0.93 1", "Chorus 3": "0.67 0.67 0.67 1",
                                 "Bridge 1": "1 1 1 1", "Bridge 2": "0.6 0.4 0.2 1", "Bridge 3": "1 0.5 0 1",
                                 "Ending": "0 1 1 1"}

# first_slide = True
# for array in root.iter('array'):
#     for RVDisplaySlide in array.findall('RVDisplaySlide'):
#         if first_slide:
#             first_slide = False
#         else:
#             array.remove(RVDisplaySlide)

    def import_template(self, template):
        self.tree = ET.parse(template)
        self.root = self.tree.getroot()

        # for member1 in self.tree.findall("./array/RVSlideGrouping/array/RVDisplaySlide"):
        #     member2 = copy.deepcopy(member1)
        #
        #     for array in self.tree.findall("./array/RVSlideGrouping/array"):
        #         array.append(member2)
        #
        #     self.tree.write("output.pro6")
        # pass

    # def import_lyrics(self, lyrics_file):


    def search_lyrics(self, song_name):
        pass
        # # Select a provider from the supported Lyrics Providers (LyricWiki, AzLyrics, Genius etc..)
        # # The default Provider is LyricWiki
        # provider = LyricWiki()
        #
        # # Fetch all lyrics from 2Pac
        # discography = provider.get_lyrics('2Pac')
        #
        # # Discography Objects and Album Objects can be iterated over.
        # for album in discography:  # album is an Album Object.
        #     print('Album: ', album.title)
        #     for song in album:  # song is a Song Object.
        #         print('Song: ', song.title)
        #         print('Lyrics: ', song.lyrics)
        #
        # # New indexing and slicing support of Discography and Album Objects
        # first_song_of_first_album = discography.albums[0].songs[0]
        # lat_two_songs_of_first_album = discography.albums[0].songs[-2:]
        #
        # # Fetch all lyrics from 2pac's album 'All eyez on me'.
        # album = provider.get_lyrics('2Pac', album='All eyes on me')
        #
        # # Fetch the lyrics from the song 'California Love' in 2pac's album 'All eyez on me'.
        # song = provider.get_lyrics('2Pac', album='All eyez on me', song='California Love)
        #
        # # Once the lyrics are fetched, you can save them on disk.
        # # The 'save()' method is implemented for Discography, Album and Song objects.
        # # By default, the lyrics are saved in {user}/Documents/lyricsmaster/
        # discography.save()
        #
        # # You can also supply a folder to save the lyrics in.
        # folder = 'c:\MyFolder'
        # discography.save(folder)
        #
        # # For anonymity, you can use a Tor Proxy to make requests.
        # # The TorController class has the same defaults as a default Tor Install.
        # provider = LyricWiki(TorController())
        # discography = provider.get_lyrics('2Pac')
        #
        # # For enhanced anonymity, the TorController can renew the the Tor ciruit for each album dowloaded.
        # # For this functionnality to work, the Tor ControlPort option must be enabled in your torrc config file.
        # # See https://www.torproject.org/docs/tor-manual.html.en for more information.
        # provider = LyricWiki(TorController(control_port=9051, password='password))
        # discography = provider.get_lyrics('2Pac')

    def generate_pro6(self):
        slide_array = None
        group_array = None

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

        # group = self.create_group(group_array, "Verse 1")
        # self.create_slide(group, "test")

        for label, section in self.lyric_instance.lyric.items():
            if not section:
                continue
            else:
                group = self.create_group(group_array, label)
                for text in section:
                    self.create_slide(group, text)

        self.tree.write("output.pro6", encoding="utf-8", xml_declaration=True)

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

        content = {
            "traditional": text,
            "simple": '简体中文',
            "english": 'English',
            "pinyin": ' '.join([''.join(s) for s in pinyin(text)])
        }
        # update UUID in RVDisplaySlide
        new_slide.attrib["UUID"] = str(uuid.uuid4()).upper()
        # update UUID in RVTextElement
        for RVTextElement in new_slide.findall("./array/RVTextElement"):
            RVTextElement.attrib["UUID"] = str(uuid.uuid4())

            for NSString_PlainText in RVTextElement.findall("./NSString[@rvXMLIvarName='PlainText']"):
                for key in keywords:
                    if NSString_PlainText.text == str(b64encode(bytes(keywords[key], encoding="utf8")), encoding="utf-8"):   # find the element of '繁體中文'
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
    pro6_generator.import_template('template.pro6')
    pro6_generator.generate_pro6()



