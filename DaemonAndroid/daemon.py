from flask import *
from base64 import *
from cryptography.fernet import Fernet
import hashlib
import base64
from diffiehellman import DiffieHellman
from os import path
import getpass
import uuid
import pickle
import json
import requests
import webbrowser
import time
import threading
from flask_cors import CORS
import urllib.parse
import termux.Notification as notification
import os

app = Flask(__name__)
CORS(app)
cloud='tushkey.mukham.in'

cloudurl="https://"+cloud
otherdevices='[]'

client_id='5173e28b-6067-4f5f-a21b-b6ba36d4aa70'
client_secret='vl78Q~r1JyrGiws6A254muEcdi4inATSGNECFdjS'

def getRand():
	return str(uuid.uuid4())

if not path.exists('devid'):
	out=open('devid', 'w')
	out.write(getRand())
	out.close()
	
in1=open('devid', 'r+')
devid=in1.read()
in1.close()

def open_new_tab(url):
	command="am start -a android.intent.action.VIEW -d "+url
	os.system(command)

def initoauth():
	open_new_tab('http://localhost:5000/initoauth')	

uname =''


def saveuserid(email):
	out=open('uname', 'w')
	out.write(email)
	out.close()

def getAllDevices():
	global otherdevices
	global uname
	
	if path.exists('uname'):
		in3=open('uname', 'r+')
		uname=in3.read()
		in3.close()
	print("Reading all devices")
	if uname=='':
		print("Blank uname")
		return
	url=cloudurl+"/newdevice"
	form_data={'uname':uname, 'devid':devid, 'dhfrom': base64.b64encode(dh_public)}
	req=requests.post(url,form_data)
	otherdevices=req.text
	print("Showing devices")
	print(otherdevices)

def senderfunc():
	if not path.exists('uname'):
		initoauth()
	else:		
		in3=open('uname', 'r+')
		uname=in3.read()
		in3.close()
	getAllDevices()
	
def receiverfunc():
	while not path.exists('uname'):
		pass
	in3=open('uname', 'r+')
	uname=in3.read()
	in3.close()
	getAllDevices()


@app.route("/initoauth", methods=["GET","POST"])
def startoauth():
	url='https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id='+client_id+'&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fgetauthn&response_mode=query&scope=user.read'
	print("Opening ",url)
	return redirect(url)

@app.route("/getauthn", methods=["GET","POST"])
def getauthn():
	global uname
	code=request.args.get('code')
	form_data={'client_id':client_id, 'scope':'user.read', 'code': '', 'redirect_uri':'http://localhost:5000/getauthn', 'grant_type': 'authorization_code', 'client_secret': client_secret}
	url1='https://login.microsoftonline.com/consumers/oauth2/v2.0/token'
	form_data['code']=code
	req1=requests.post(url1, form_data)
	js1=json.loads(req1.text)
	acc=js1['access_token']
	url2='https://graph.microsoft.com/v1.0/me'
	headers={'Authorization': "Bearer "+acc, 'Content-Type': 'application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8'}
	req2=requests.get(url2, headers=headers)
	js2=json.loads(req2.text)
	email	=js2['userPrincipalName']
	uname=email
	saveuserid(email)
	try:
		getAllDevices()
	except:
		pass
	print("Logged in")
	return "Logged in as "+email

if not path.exists('diffiehellman'):
	out=open('diffiehellman', 'wb')
	dh=DiffieHellman(group=14, key_bits=540)
	pickle.dump(dh,out)
	out.close()
	
in2=open('diffiehellman', 'rb')
dh=pickle.load(in2)
in2.close()
print("Read Diffie Hellman")
dh_public=dh.get_public_key()

def getAESKey(dh_public2):
	dh_shared=dh.generate_shared_key(base64.b64decode(dh_public2))
	hlib=hashlib.md5()
	hlib.update(dh_shared)
	x=base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))
	key=Fernet(x)
	print("Generated AES")
	return key
	


def noti(dom):
	notification.notify(
		title="TUSHkey",
		content="New TUSHKey found for "+dom,
		)

def getTokens():
	print("Reading all tokens")
	url=cloudurl+"/gettokens"
	form_data={'devid': devid}
	resp=requests.post(url, form_data)
	xx=json.loads(resp.text)
	devices=json.loads(otherdevices)
	for tok in xx:
		token=tok['token']
		sender=tok['sender']
		for dev in devices:
			if dev['devid']==sender:
				aeskey=getAESKey(dev['dhpub'])
				decr=aeskey.decrypt(token.encode()).decode()
				decr=urllib.parse.unquote_plus(decr)
				parsed_url = urllib.parse.urlparse(decr)
				domain=parsed_url.netloc
				noti(domain)
				open_new_tab(decr)
	

@app.route("/handletoken", methods=["GET","POST"])
def handletoken():
	print("Received token from RP")
	token=request.args.get('token')
	print(token)
	while True:
		try:
			getAllDevices()
			devices=json.loads(otherdevices)
			print(devices)
			for dev in devices:
				while True:
					devidrec=dev['devid']
					dhpubrec=dev['dhpub']
					aeskey=getAESKey(dhpubrec)
					encr=aeskey.encrypt(token.encode()).decode()
					print(encr)
					form_data={'senderid':devid, 'receiverid':devidrec, 'token':encr}
					resp=requests.post(cloudurl+"/addtoken", form_data)
					print(resp.text)
					if resp.text == "Token added":
						break
			break
		except:
			pass
	return 'success'
		
def handleSender():
	senderfunc()
	app.run(host='0.0.0.0', port=5000, debug=True)
	
def handleReceiver():
	receiverfunc()
	while True:
		try:
			getAllDevices()
			getTokens()
			time.sleep(3)
		except:
			pass
		
