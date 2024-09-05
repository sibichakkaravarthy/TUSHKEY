import pyodbc
import json
from blobops import *
import collections

server='tushkeydatabase.database.windows.net'
database='tushkeydb'
username='vm_user'
password='{Password12345*}'
driver='{ODBC Driver 17 for SQL Server}'

conn=pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor=conn.cursor()

def createDeviceTable():
	try:
		cursor.execute("CREATE TABLE [Device](uname VARCHAR(50), devid VARCHAR(50))")
		cursor.commit()
	except:
		pass
		
def createTokenTable():
	try:
		cursor.execute("CREATE TABLE [Encrtokens](uname VARCHAR(50), tokenblob VARCHAR(50), devidsender VARCHAR(50), devidrec VARCHAR(50))")
		cursor.commit()
	except:
		pass
		
def addDevice(uname, devid):
	try:
		cursor.execute("INSERT INTO [Device] VALUES (?,?)", uname, devid)
		cursor.commit()
	except:
		addDevice(uname, devid)
				
def addToken(tokenblob, devidsender, devidrec):
	try:
		cursor.execute("SELECT uname FROM [Device] WHERE devid=?", devidsender)
		uname=cursor.fetchone()[0]
		cursor.commit()
		cursor.execute("INSERT INTO [Encrtokens] VALUES (?,?,?,?)", uname, tokenblob, devidsender, devidrec)
		cursor.commit()
	except:
		addToken(tokenblob, devidsender, devidrec)
				
def deleteToken(tokenblob):
	try:
		cursor.execute("DELETE FROM [Encrtokens] WHERE tokenblob=?", tokenblob)
		cursor.commit()
	except:
		pass
		
def retrieveDHKeys(devid):
	#try:
	cursor.execute("SELECT uname FROM [Device] WHERE devid=?",devid)
	uname=cursor.fetchone()[0]
	print(uname)
	cursor.commit()
	cursor.execute("SELECT devid FROM [Device] WHERE uname=?", uname)
	retvalue=cursor.fetchall()
	cursor.commit()
	object_list=[]
	for x in retvalue:
		if not x[0]==devid:
			d=collections.OrderedDict()
			d['devid']=x[0]
			print(d['devid'])
			d['dhpub']=getBlob(x[0])
			print(d['dhpub'])
			object_list.append(d)
	j=json.dumps(object_list)
	return j
	#except:
	#	return "[]"
		
def getSingleDH(devid):
	try:
		dhpub=getBlob(devid)
		return dhpub
	except:
		return "00"
		
def retrieveTokens(devidrec):
	try:
		cursor.execute("SELECT tokenblob, devidsender FROM [Encrtokens] WHERE devidrec=?", devidrec)
		retvalue=cursor.fetchall()
		cursor.commit()
		object_list=[]
		for x in retvalue:
			d=collections.OrderedDict()
			d['token']=getBlob(x[0])
			d['sender']=x[1]
			deleteToken(x[0])
			object_list.append(d)
		j=json.dumps(object_list)
		return j
	except:
		return "[]"
		
def createDb():
	createDeviceTable()
	createTokenTable()

createDb()

def erase():
	cursor.execute("DELETE FROM [Device]")
	cursor.execute("DELETE FROM [Encrtokens]")
	cursor.commit()