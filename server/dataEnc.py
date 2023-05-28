#import genKeys as GK
import pickle
import rsa

"""
Data File Structure -->

{
	'username': {
		'PASS': user_password,
		'PUBKEY': public key
		'google.com': [
			["ccabitter@gmail.com", password]
			["cameron.bitter@berwickacademy.org", password]
		]
	}
}
					<--
"""

def encryptMSG(msg):
    return rsa.encrypt(msg.encode(), pubKey)

def decryptMSG(msg):
    return rsa.decrypt(msg, privKey).decode()


with open("keys/id_rsa.pub", "rb") as f:
	pubKey = pickle.load(f)


try:
	with open("keys/id_rsa", "rb") as f:
		privKey = pickle.load(f)

except FileNotFoundError:
	pass


def encryptData(data):

	encodedData = {}
	#testDict = {}

	for user in data:
		userENC = encryptMSG(user)
		encodedData[userENC] = {}

		#testDict[user] = {}

		for item in data[user]:
			itemENC = encryptMSG(item)

			if item == "PUBKEY":
				encodedData[userENC][itemENC] = data[user][item] # don't need to encode public key
				#testDict[user][item] = data[user][item]

			elif item == "PASS": 
				encodedData[userENC][itemENC] = encryptMSG(str(data[user][item]))
				#testDict[user][item] = str(data[user][item])

			else:
				encodedData[userENC][itemENC] = []
				#testDict[user][item] = []

				try:
					for i in range(len(data[user][item])):

						username_pass = [encryptMSG(data[user][item][i-1][0]), encryptMSG(data[user][item][i-1][1])]

						encodedData[userENC][itemENC].append(username_pass)
						#testDict[user][item].append([data[user][item][i-1][0], data[user][item][i-1][1]])


				except IndexError as e:
					print(e)


	return encodedData


def decryptData(data):

	decodedData = {}
	#testDict = {}

	for userENC in data:
		user = decryptMSG(userENC)
		decodedData[user] = {}

		#testDict[user] = {}

		for itemENC in data[userENC]:
			item = decryptMSG(itemENC)

			if item == "PUBKEY":
				decodedData[user][item] = data[userENC][itemENC] # don't need to encode public key
				#testDict[user][item] = data[user][item]

			elif item == "PASS": 
				decodedData[user][item] = decryptMSG((data[userENC][itemENC]))
				#testDict[user][item] = str(data[user][item])

			else:
				decodedData[user][item] = []
				#testDict[user][item] = []

				try:
					for i in range(len(data[userENC][itemENC])):

						username_pass = [decryptMSG(data[userENC][itemENC][i-1][0]), decryptMSG(data[userENC][itemENC][i-1][1])]

						decodedData[user][item].append(username_pass)
						#testDict[user][item].append([data[user][item][i-1][0], data[user][item][i-1][1]])


				except IndexError as e:
					print(e)


	return decodedData

