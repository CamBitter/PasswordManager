import rsa
import pickle


# Generates new private / public key pair

def genKeys():
	pubKey, privKey = rsa.newkeys(2048)


	with open("server/keys/id_rsa.pub", "wb") as  f:
	    #pubKey = pickle.load(f)
	    pickle.dump(pubKey, f)

	with open("server/keys/id_rsa", "wb") as  f:
	    #pubKey = pickle.load(f)
	    pickle.dump(privKey, f)

	with open("client/keys/id_rsa.pub", "wb") as  f:
	    #pubKey = pickle.load(f)
	    pickle.dump(pubKey, f)

	with open("client/keys/id_rsa", "wb") as f:
	    #privKey = pickle.load(f)
	    pickle.dump(privKey, f)



	return pubKey