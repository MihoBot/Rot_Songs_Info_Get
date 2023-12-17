import re
import httpx
import sqlite3
import time

headers={
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
					  "Chrome/89.0.4389.128 Safari/537.36"}

def Get_Rotaeno_List():
	url='https://wiki.rotaeno.cn/index.php'
	params={'title':'曲目列表','action':'raw'}
	try:
		req=httpx.get(url, headers=headers, params=params, timeout=5)
		s=req.text
		return s
	except Exception as e:
		print(e)
		return 'TimeOut'

def Get_Rotaeno_Data(SongName):
	url='https://wiki.rotaeno.cn/'+SongName.replace(" ","_")
	try:
		req=httpx.get(url, headers=headers, timeout=5)
		s=req.text
		return s
	except Exception as e:
		print(e)
		return 'TimeOut'

def Get_Rotaeno_Pic(Url):
	try:
		req=httpx.get(Url, headers=headers, timeout=None)
		p=req.content
		return p
	except Exception as e:
		print(e)
		return None

def Get_Rotaeno_Song(PicName):
	url='https://wiki.rotaeno.cn/index.php'
	params={'title':'File:'+PicName}
	try:
		req=httpx.get(url, headers=headers, params=params, timeout=None)
		s=req.text
		File=open("RotPic.txt",mode='w',encoding='utf-8')
		File.wirte(s)
	except Exception as e:
		print(e)
		return None

def Judge_Text(Text):
	if (Text=='曲目信息')|(Text=='曲包'):
		return False
	if (Text=='曲师')|(Text=='画师'):
		return False
	if (Text=='来源')|(Text=='时长'):
		return False
	if (Text=='谱面信息')|(Text=='等级'):
		return False
	if (Text=='谱师')|(Text=='Note数量'):
		return False
	if (Text=='更新时间')|(Text=='更新版本'):
		return False
	if (Text=='难度')|(Text=='难度I')|(Text=='难度II')|(Text=='难度III')|(Text=='难度IV'):
		return False
	if (Text=='难度Ⅳ')|(Text=='难度Ⅲ')|(Text=='难度Ⅱ'):
		return False
	return True

def Data_Process():
	TextTmp='''INSERT INTO songinfo (song_name,
				songpack,
				composer,
				illustrator,
				ChartDesigner,
				"Note I",
				"Note II",
				"Note III",
				"Note IV",
				"Level I",
				"Level II",
				"Level III",
				"Level IV",
				cover
				) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
	Connect=sqlite3.connect('data\Rotaeno\Rotaeno Test.db')
	Cur=Connect.cursor()
	File=open("Rotaeno.txt",mode='r',encoding='utf-8')
	Text1=''
	Text2=''
	TextPic=''
	Inf1=[]
	Inf2=[]
	InfPic=[]
	Final=[]
	Tmp=[]
	Data1=File.readlines()
	for Line in Data1:
		IsFind=Line.find('mw-content-text')
		if IsFind!=-1:
			Text1=Line
		IsFind=Line.find('<table class="rotable"><tbody><tr><th>')
		if IsFind!=-1:
			Text2=Line
	if Text1!='':
		Pattern=r'>.*?<'
		Inf1=re.findall(Pattern,Text1)
	while '><' in Inf1:
		Inf1.remove('><')
	while '><' in Inf2:
		Inf2.remove('><')
	for Text in Inf1:
		if (Text!='><')&(Text!='>Rotaeno Sound Collection<')&Judge_Text(Text.replace('<','').replace('>','')):
			Text=Text.replace('<','').replace('>','')
			Text=Text.replace('amp;','')
			Final.append(Text)
	if Text2!='':
		Pattern=r'>.*?<'
		Inf2=re.findall(Pattern,Text2)
	for Text in Inf2:
		if (Text!='><')&Judge_Text(Text.replace('<','').replace('>','')):
			Text=Text.replace('<','').replace('>','')
			Final.append(Text)
	# for Text in Final:
	# 	print(Text)
	Cur=Connect.cursor()
	Cur.execute("SELECT song_name FROM songinfo WHERE song_name=?;",(Final[0],))
	Res=Cur.fetchone()
	print(Res)
	if(Res!=None):
		return
	Pos1=Text1.find('Note数量')+15
	Pos2=Text1.find('更新时间')-18
	# print(Text1[Pos1:Pos2])
	Tmp=Text1[Pos1:Pos2].split("</td><td>")
	NoteList=['Un' if Text=='' else Text for Text in Tmp]
	if Final[1]=='未指定图片':
		del Final[1]
		Final.insert(3,'没有曲绘要什么画师！')
	if Final[1][:3]=='en:':
		del Final[1]
	del Final[4:5]
	del Final[5:9]
	if(Final[-1][0]!='v'):
		del Final[5:-4]
	else:
		del Final[-2:]
		Final.append('我不知道')
		Final.append('我不知道')
		Final.append('我不知道')
		Final.append('我不知道')
	for Text in Final:
		print(Text)
	# print(Text1)
	if Text1!='':
		Pattern=r'/File:.*?"'
		if Text1.find('File:')!=-1:
			InfPic=re.findall(Pattern,Text1)[0][6:-1]
		else:
			InfPic='没有图片，自己问Wiki工作人员要（怒气MAX）'
	# print(InfPic)	
	Cur.execute(TextTmp,(Final[0],Final[1],Final[2],Final[3],Final[4],NoteList[0],NoteList[1],NoteList[2],NoteList[3],Final[5],Final[6],Final[7],Final[8],InfPic))
	Connect.commit()
	Connect.close()
	# for Text1 in Data:
	# 	print(Text1)

# Data=Get_Rotaeno_Data()
# File=open("Rotaeno.txt","w",encoding="utf-8")
# File.write(Data)
# Data_Process()

def TotalGet():
	Text=Get_Rotaeno_List()
	# print(Text)
	Patterns=r'\[\[[^文件]*\]\]'
	SongList=re.findall(Patterns,Text)
	time.sleep(2)
	for Song in SongList:
		print(Song[2:-2])
		Song.replace('别れの序曲','別れの序曲')
		Data=Get_Rotaeno_Data(Song[2:-2].lstrip())
		if Data=='TimeOut':
			print(Song[2:-2]+':Fuck')
			continue
		File=open("Rotaeno.txt",mode='w',encoding='utf-8')
		File.write(Data[10000:])
		File.close()
		Data_Process()
		# break
		time.sleep(2)

print("Start!")
TotalGet()