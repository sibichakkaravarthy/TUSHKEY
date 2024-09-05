from flask import *
import uuid
from dbops import *
from blobops import *


app = Flask(__name__)

def getRand():
	return str(uuid.uuid4())
	
@app.route("/newdevice", methods=['POST','GET'])
def newDevice():
	uname=request.form['uname']
	devid=request.form['devid']
	dhpub=request.form['dhfrom']
	dhpubex=getSingleDH(devid)
	print('Adding device')
	if not dhpubex==dhpub: 
		writeBlob(dhpub, devid)
		addDevice(uname, devid)
		print("Device added "+devid)
	x=getkeys(devid)
	return x
		
@app.route("/addtoken", methods=['POST', 'GET'])
def addtoken():
	senderid=request.form['senderid']
	receiverid=request.form['receiverid']
	token=request.form['token']
	blobid=getRand()
	writeBlob(token, blobid)
	addToken(blobid, senderid, receiverid)
	return "Token added"
	
def getkeys(devid):
	x=retrieveDHKeys(devid)
	return x
	
@app.route("/gettokens", methods=['POST', 'GET'])
def getTokens():
	devid=request.form['devid']
	x=retrieveTokens(devid)
	return x
	
if __name__ == '__main__':
   app.run(host='0.0.0.0', debug = True)