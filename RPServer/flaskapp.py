from __future__ import print_function, absolute_import, unicode_literals

from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData
from fido2 import cbor
from flask import *
import pickle
import os
import uuid
from os import path
from dbops import *
import urllib.parse

rpid='testrp.mukham.in'
filepth='/home/vm_user/Files'

app = Flask(__name__, static_url_path="")

if not path.exists(filepth+'/appsecret.pkl'):
	outp3=open(filepth+'/appsecret.pkl','wb')
	pickle.dump(os.urandom(32),outp3,pickle.HIGHEST_PROTOCOL)
	outp3.close()

inp3=open(filepth+'/appsecret.pkl', 'rb')
app.secret_key = pickle.load(inp3)
inp3.close()

rp = PublicKeyCredentialRpEntity(rpid, "Test RP")
server = Fido2Server(rp)


# Registered credentials are stored globally, in memory only. Single user
# support, state is lost when the server terminates.
credentials = []

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template("index.html")
	
@app.route("/signupreg", methods=["GET","POST"])
def signupreg():
	return render_template("signupreg.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
	uname=request.form['username']
	if userExist(uname):
		return render_template("error.html", reason="User already exists")
	name=request.form['name']
	blobid=str(uuid.uuid4())
	addUser(uname, name, blobid)
	return render_template("register.html", uname=uname)
	
@app.route("/login", methods=["GET", "POST"])
def login():
	return render_template("loginform.html")
	
@app.route("/signin", methods=["GET", "POST"])
def signin():
	uname=request.form['username']
	if not userExist(uname):
		return render_template("error.html", reason="User doesnt exist")
	return render_template("authenticate.html", uname=uname)

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
	uname=request.args.get('username')
	name=getName(uname)
	return render_template("dashboard.html", name=name, uname=uname)

@app.route("/api/register/begin", methods=["GET","POST"])
def register_begin():
    uname=request.args.get('username')
    credentials=read_key(uname)
    registration_data, state = server.register_begin(
        {
            "id": b"user_id",
            "name": uname,
            "displayName": uname,
            "icon": "https://example.com/image.png",
        },
        credentials,
        user_verification="discouraged",
        authenticator_attachment="platform",
    )

    session["state"] = state
    print("\n\n\n\n")
    print(registration_data)
    print("\n\n\n\n")
    return cbor.encode(registration_data)


@app.route("/api/register/complete", methods=["GET","POST"])
def register_complete():
    uname=request.args.get('username')
    credentials=read_key(uname)
    data = cbor.decode(request.get_data())
    client_data = ClientData(data["clientDataJSON"])
    att_obj = AttestationObject(data["attestationObject"])
    print("clientData", client_data)
    print("AttestationObject:", att_obj)

    auth_data = server.register_complete(session["state"], client_data, att_obj)

    credentials.append(auth_data.credential_data)
    save_key(credentials,uname)
    print("REGISTERED CREDENTIAL:", auth_data.credential_data)
    return cbor.encode({"status": "OK"})


@app.route("/api/authenticate/begin", methods=["GET","POST"])
def authenticate_begin():
    uname=request.args.get('username')
    credentials=read_key(uname)
    if not credentials:
        abort(404)

    auth_data, state = server.authenticate_begin(credentials)
    session["state"] = state
    return cbor.encode(auth_data)


@app.route("/api/authenticate/complete", methods=["GET","POST"])
def authenticate_complete():
    uname=request.args.get('username')
    credentials=read_key(uname)
    if not credentials:
        abort(404)

    data = cbor.decode(request.get_data())
    credential_id = data["credentialId"]
    client_data = ClientData(data["clientDataJSON"])
    auth_data = AuthenticatorData(data["authenticatorData"])
    signature = data["signature"]
    print("clientData", client_data)
    print("AuthenticatorData", auth_data)

    server.authenticate_complete(
        session.pop("state"),
        credentials,
        credential_id,
        client_data,
        auth_data,
        signature,
    )
    print("ASSERTION OK")
    print("Authenticated to "+str(request.remote_addr))
    return cbor.encode({"status": "OK"})
    
@app.route("/generatetoken", methods=["GET","POST"])
def newtoken():
	uname=request.form['username']
	token=str(uuid.uuid4())
	addToken(uname, token)
	return urllib.parse.quote_plus("https://"+rpid+"/signupwithtoken?token="+token)
	
@app.route("/signupwithtoken", methods=["GET","POST"])
def signupwithtoken():
	token=request.args.get('token')
	uname=getUname(token)
	#deleteToken(token)
	return render_template("register.html", uname=uname)

def read_key(uname):
	try:
		blobid=getBlobId(uname)
		fln=open(filepth+'/'+blobid,'rb')
		creds=pickle.load(fln)
		fln.close()
		return creds
	except:
		return []
		
def save_key(credentials, uname):
	blobid=getBlobId(uname)
	print("Saving")
	print(blobid)
	fln=open(filepth+'/'+blobid, 'wb')
	pickle.dump(credentials, fln)
	fln.close()
	print('saved')


if __name__ == "__main__":
    print(__doc__)
    app.run(ssl_context="adhoc", debug=False, port=8080)