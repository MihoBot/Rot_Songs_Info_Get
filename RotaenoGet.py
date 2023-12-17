import httpx
import sqlite3
import os
import time

from lxml import etree

Trash = ("曲目信息", "铺面信息", "难度", "等级", "Note数量")

DifDic = {}


def Get_Rotaeno_Dif():
    url = "https://wiki.rotaeno.cn/%E5%AE%9A%E6%95%B0%E8%AF%A6%E8%A1%A8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
    }
    try:
        req = httpx.get(url, headers=headers, timeout=5)
        s = req.text
        return s
    except Exception as e:
        print(e)
        return None


def GetWholeData(Web):
    url = "https://wiki.rotaeno.cn/" + Web
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
    }
    try:
        req = httpx.get(url, headers=headers, timeout=5)
        s = req.text
        return s
    except Exception as e:
        print(e)
        return None


def PicGet(PicWeb):
    url = "https://wiki.rotaeno.cn/" + PicWeb
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
    }
    try:
        req = httpx.get(url, headers=headers, timeout=5)
        s = req.content
        return s
    except Exception as e:
        print(e)
        return None


def Str2HTML_Dif(RawStr):
    # print(type(RawStr))
    HTML = etree.HTML(RawStr, None)
    Temp = HTML.xpath("//*[@id='mw-content-text']/div[1]/table/tbody//text()")
    # print(Temp)
    return Temp


def Str2HTML(RawStr):
    # print(type(RawStr))
    HTML = etree.HTML(RawStr, None)
    Temp = HTML.xpath("//*[@id='mw-content-text']/div[1]/table/tbody/tr/td/a/@href")
    # print(Temp)
    return Temp


def PicWebGet(PicPath):
    url = "https://wiki.rotaeno.cn/" + PicPath
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
    }
    try:
        req = httpx.get(url, headers=headers, timeout=5)
        s = req.text
        HTML = etree.HTML(s, None)
        web = HTML.xpath("//*[@id='file']/a/@href")[0]
        print(web)
        return web
    except Exception as e:
        print(e)
        return None


def DataStorage(Str):
    File = open("DataGetPy\\Log\\Rotaeno.cache", mode="w", encoding="utf-8")
    File.write(Str)


def ReadCache():
    File = open("DataGetPy\\Log\\Rotaeno.cache", mode="r", encoding="utf-8")
    Str = File.read()
    return Str


def SongStorage(SongName, SongData):
    file = open(
        f"DataGetPy\\Cache\\Rotaeno\\{SongName}.cache", mode="w", encoding="utf-8"
    )
    # try:
    file.write(SongData)
    # except Exception as e:


def SongRead(SongName):
    file = open(
        f"DataGetPy\\Cache\\Rotaeno\\{SongName}.cache", mode="r", encoding="utf-8"
    )
    SongData = file.read()
    return SongData


def CacheDelete(SongName):
    try:
        os.remove(f"DataGetPy\\Cache\\Rotaeno\\{SongName}.cache")
    except Exception as e:
        print(e)


def HTML2Data(HTML, SongName, SongWeb):
    try:
        Data = HTML.xpath("//*[@id='mw-content-text']/div[1]/table[1]/tbody//text()")
        Try = Data[0]
        return Data
    except IndexError as e:
        CacheDelete(SongName=SongName)
        SongStorage(SongName=SongName, SongData=GetWholeData(Web=SongWeb))
        HTML = etree.HTML(SongRead(SongName=SongName), None)
        Data = HTML.xpath("//*[@id='mw-content-text']/div[1]/table[1]/tbody//text()")
        return Data
    except Exception as e:
        CacheDelete(SongName=SongName)
        print("缓存出错，请重试以重新读取")
        raise (e)


def DataProcess(TempData, SongName, SongWeb):
    HTML = etree.HTML(TempData, None)
    # print(HTML)
    Data = HTML2Data(HTML=HTML, SongName=SongName, SongWeb=SongWeb)
    if Data == Exception:
        return
    # print(Data)
    Name = Data[0]
    Info = {
        "Name": Name,
        "Collection": "",
        "Composer": "",
        "Artist": "",
        "Charter": "",
        "Length": "",
        "Dif": ["", "", "", ""],
        "Note": ["Un", "Un", "Un", "Un"],
        "Cover": "",
    }
    for Index in range(1, len(Data), 1):
        if Data[Index] == "曲包":
            Info["Collection"] = Data[Index + 1]
        if Data[Index] == "曲师":
            Info["Composer"] = Data[Index + 1]
        if Data[Index] == "画师":
            Info["Artist"] = Data[Index + 1]
        if Index + 1 < len(Data):
            if (Data[Index] == "时长") & (Data[Index + 1] != "谱面信息"):
                Info["Length"] = Data[Index + 1]
            elif Data[Index] == "时长":
                Info["Length"] = "Un"
        if Data[Index] == "谱师":
            Info["Charter"] = Data[Index + 1]
        if Data[Index] == "Note数量":
            TempIndex = Index
            while Data[TempIndex - 1] != "等级":
                TempIndex -= 1
                Info["Dif"][4 - Index + TempIndex] = Data[TempIndex]
        if Data[Index] == "更新时间":
            TempIndex = Index
            while Data[TempIndex - 1] != "Note数量":
                TempIndex -= 1
                if Data[TempIndex] != "0":
                    Info["Note"][4 - Index + TempIndex] = Data[TempIndex]
                else:
                    Info["Note"][4 - Index + TempIndex] = "Un"
    # print(Info)
    return Info


DBPath = "data\\Rotaeno\\Rotaeno New.db"


def DBStorage(Info):
    Connect = sqlite3.connect(DBPath)
    Cur = Connect.cursor()
    Cur.execute(
        """INSERT INTO SongData ("song_name",
                "songpack",
                "composer",
                "illustrator",
                "Charter",
                "Level I",
                "Level II",
                "Level III",
                "Level IIII",
                "Note I",
                "Note II",
                "Note III",
                "Note IIII",
                "cover"
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            Info["Name"],
            Info["Collection"],
            Info["Composer"],
            Info["Artist"],
            Info["Charter"],
            Info["Dif"][0],
            Info["Dif"][1],
            Info["Dif"][2],
            Info["Dif"][3],
            Info["Note"][0],
            Info["Note"][1],
            Info["Note"][2],
            Info["Note"][3],
            Info["Cover"],
        ),
    )
    Connect.commit()
    Connect.close()


def SongIteration():
    TempData = Str2HTML(ReadCache())
    DifData = Str2HTML_Dif(ReadCache())
    # print(DifData)
    for Index in range(6, len(DifData), 5):
        DifDic[DifData[Index]] = DifData[Index + 1 : Index + 5]
        # break
    # print(DifDic)
    for Text in TempData:
        print(Text)
    TempPicName = ""
    for Text in TempData:
        if Text[:6] == "/File:":
            PicPath = Text[1:]
            PicName = PicPath[5:].replace("%", "").replace("/", "")
            TempPicName = PicName
            if not os.path.exists("data\\Rotaeno\\cover\\" + PicName):
                PicRawData = PicGet(PicWeb=PicWebGet(PicPath=PicPath))
                file = open("data\\Rotaeno\\cover\\" + PicName, mode="wb")
                file.write(PicRawData)
                file.close()
                time.sleep(3)
            # print(PicPath)
            continue
        # print(str(Text)+':')
        # print(Text)
        SongName = Text[1:].replace("%", "").replace("/", "")
        # print(SongName)
        if not os.path.exists(f"DataGetPy\\Cache\\Rotaeno\\{SongName}.cache"):
            SongRawData = GetWholeData(Text[1:])
            SongStorage(SongName=SongName, SongData=SongRawData)
            time.sleep(3)
        Temp = SongRead(SongName=SongName)
        Info = DataProcess(TempData=Temp, SongName=SongName, SongWeb=Text[1:])
        Info["Cover"] = "data\\Rotaeno\\cover\\" + TempPicName
        Info["Cover"] = Info["Cover"].replace("\\", "/")
        DBStorage(Info)
        # break


def Main():
    if os.path.isfile("DataGetPy\\Log\\Rotaeno.cache"):
        Opt = input("检测到有网页缓存，是否使用缓存？（是 Y & 否 N）")
        if Opt == "Y":
            Flag = 0
        else:
            Flag = 1
    else:
        Flag = 1
    if Flag == 1:
        RawData = Get_Rotaeno_Dif()
        DataStorage(RawData)
    SongIteration()
    # DataProcess(TempData)


Main()
