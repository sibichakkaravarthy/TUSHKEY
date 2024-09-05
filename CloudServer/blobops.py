path='/home/vm_user/Files'

def writeBlob(content, blobid):
	fl=open(path+"/"+blobid, "w")
	fl.write(content)
	fl.close()
	
def getBlob(blobid):
	fl=open(path+"/"+blobid, "r+")
	x=fl.read()
	fl.close()
	return x