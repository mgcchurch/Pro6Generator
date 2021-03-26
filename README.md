# Pro6Generator
A tool to create Pro6 file from text file

### How does Pro6Generator work?
Before using the tool, you need to prepare your lyrics file and a template file of the ProPresenter6, and the template file should just contain one slide in which 4 different text boxes are added and type the words "English" "简体中文" "繁體中文" and "Pinyin" in those text boxes. In the repository, there is a sample file "template.pro6". The lyrics file should follow the format like the lyrics.txt file

### Who uses Pro6Generator?
Anyone who hope to convert the text lyrics to pro6 files 

### Getting started

#### Convert single lyrics file

```shell
$ python pro6generator.py --template template.pro6 --lyricsfile lyrics.txt
```
or 
```shell
$ python pro6generator.py -t template.pro6 -l lyrics.txt
```

#### Convert a folder of lyrics file

```shell
$ python pro6generator.py --template template.pro6 --lyricsfolder lyrics_folder
```
or 
```shell
$ python pro6generator.py -t template.pro6 -d lyrics_folder
```
