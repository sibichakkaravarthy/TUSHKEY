import pyodbc
import json
import time

server='tushkeydatabase.database.windows.net'
database='tushkeydb'
username='vm_user'
password='{Password12345*}'
driver='{ODBC Driver 17 for SQL Server}'

conn=pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor=conn.cursor()

def createUsersTable():
	try:
		cursor.execute("CREATE TABLE [Users] (uname VARCHAR(50), name VARCHAR(50), blobid VARCHAR(50))")
		cursor.commit()
	except:
		pass
		
def createTokensTable():
	try:
		cursor.execute("CREATE TABLE [Tokens] (uname VARCHAR(50), token VARCHAR(50), issuetime VARCHAR(50))")
		cursor.commit()
	except:
		pass
		
def addUser(uname, name, blobid):
	try:
		cursor.execute("INSERT INTO [Users] VALUES(?,?,?)", uname, name, blobid)
		cursor.commit()
	except:
		pass
		
def addToken(uname, token):
	try:
		ts=str(time.time())
		cursor.execute("INSERT INTO [Tokens] VALUES (?,?,?)", uname, token, ts)
		cursor.commit()
	except:
		pass
		
def getBlobId(uname):
	try:
		cursor.execute("SELECT blobid FROM [Users] WHERE uname=?", uname)
		ret=cursor.fetchone()[0]
		cursor.commit()
		return ret
	except:
		return ""
		
def getName(uname):
	try:
		cursor.execute("SELECT name FROM [Users] WHERE uname=?", uname)
		ret=cursor.fetchone()[0]
		cursor.commit()
		return ret
	except:
		return ""
		
def userExist(username):
	x=getBlobId(username)
	return not x==""
			
def getUname(token):
	if not tvalid(token):
		print('invalid')
	try:
		print("Seeing db")
		cursor.execute("SELECT uname FROM [Tokens] WHERE token=?", token)
		ret=cursor.fetchone()[0]
		cursor.commit()
		return ret
	except:
		return ''
		
def deleteToken(token):
	try:
		cursor.execute("DELETE FROM [Tokens] WHERE token=?", token)
		cursor.commit()
	except:
		pass
		
def tvalid(token):
	try:
		ts=str(time.time())
		cursor.execute("SELECT issuetime FROM [Tokens] WHERE token=?", token)
		its=cursor.fetchone()[0]
		x=float(ts)-float(its)
		print("Valid token")
		return x>300
	except:
		print("Invalid token")
		return False
	
		
def init():
	createUsersTable()
	createTokensTable()
	
init()		

def erase():
	cursor.execute("DELETE FROM [Users]")
	cursor.execute("DELETE FROM [Tokens]")
	cursor.commit()
