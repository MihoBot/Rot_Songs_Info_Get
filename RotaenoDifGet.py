import httpx
import sqlite3
import os

from lxml import etree


def Get_Rotaeno_Dif():
    url = "https://wiki.rotaeno.cn/%E5%AE%9A%E6%95%B0%E8%AF%A6%E8%A1%A8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
    }
    try:
        req = httpx.get(url, headers=headers, timeout=2)
        s = req.text
        return s
    except Exception as e:
        print(e)
        return None


def DataStorage(Str):
    File = open("DataGetPy\\Log\\RotaenoDif.cache", mode="w", encoding="utf-8")
    File.write(Str)


def ReadCache():
    File = open("DataGetPy\\Log\\RotaenoDif.cache", mode="r", encoding="utf-8")
    Str = File.read()
    return Str


def Str2HTML(RawStr):
    print(type(RawStr))
    HTML = etree.HTML(RawStr, None)
    Temp = HTML.xpath("//*[@id='mw-content-text']/div[1]/table/tbody//text()")
    # print(Temp)
    return Temp


DBPath = "data\\Rotaeno\\Rotaeno New.db"


def DataProcess(TempData):
    Connect = sqlite3.connect(DBPath)
    Cur = Connect.cursor()
    del TempData[:6]
    for Index in range(0, len(TempData), 5):
        Arg = TempData[Index : Index + 5]
        print(Arg)
        Cur.execute(
            f'''UPDATE SongData SET "Level I"={Arg[1]},"Level II"={Arg[2]},"Level III"={Arg[3]},"Level IIII"={Arg[4]} WHERE song_name="{Arg[0]}"''',
        )
        # Cur.execute(
        #     f'''SELECT Note1,Note2,Note3,Note4 FROM SongData WHERE Name="{Arg[0]}"'''
        # )
        # Indexs = ("Note1", "Note2", "Note3", "Note4")
        # Data = Cur.fetchone()
        # print(Data)
        # for Index in range(0, len(Indexs)):
        #     if Data[Index] == "0":
        #         Cur.execute(
        #             f'''UPDATE SongData SET {Indexs[Index]}="Un" WHERE Name="{Arg[0]}"'''
        #         )
        # break
    Connect.commit()
    Connect.close()


def Main():
    if os.path.isfile("DataGetPy\\Log\\RotaenoDif.cache"):
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
    TempData = Str2HTML(ReadCache())
    DataProcess(TempData)


Main()
