import genKeys as gK
import time
import pickle
import socket

import configparser


# get inputs
name = input("Name: ")
passw = input("Create password: ")
print("Generating keys . . . ")


# make the public key
pubKey = gK.genKeys()

import dataEnc as encoder



# make the dictionary
data = {
	name: {
		'PASS': passw,
		'PUBKEY': pubKey,
	}
}
print("done . . . creating file . . .")


with open("server/data.dat", "wb") as  f:
	pickle.dump(encoder.encryptData(data), f)

print("done.")

while True:
	try:
		host = str(input("Host IP Address (leave blank for localhost [127.0.0.1], or enter 'host' for current computer IP address): "))
		if host == "":
			host = "127.0.0.1"
		elif host == "host":
			host = socket.gethostbyname(socket.gethostname()) 

		break

	except:
		print("Enter a valid host: must be string IP address")

while True:
	try:
		port = int(input("Port: "))
		if len(str(port)) == 5:
			break
		else:
			i = 5/0

	except:
		print("Enter a valid port: must be 5 digit integer")

while True:
	try:
		header_length = (input("Header length (leave blank for default): "))
		if header_length == "" or header_length == " ":
			header_length = 10

		else:
			header_length = int(header_length)

		break

	except:
		print("Enter a valid header length: must be integer")


config = configparser.ConfigParser()
config['CONFIG'] = {'HOST': host,
					'PORT': port,
					'HEADER_LENGTH': header_length}

with open('server/config.ini', 'w') as configfile:
	config.write(configfile)

with open('client/config.ini', 'w') as configfile:
	config.write(configfile)

print("Done.")


# 	>--< FORMAT >--<
# {
# 	'Cam': {
# 		'PASS': '121324', 
# 		'PUBKEY': PublicKey(17917520893563208056769980370428525825987764423760479568912306734542690988627953113011423367539389162838897468526927256894470620904761185565627083508482067033323112572618636613385443299455452998178749053046617325840936119888995621960786844154508921123465696489163191586255651128931997918438658106549778422976652566437237878856765759332863918283828387163456672383476949910428521631996881837351975608005423751006239246337089285433045627268847867948154691558643741566144965169892747128111966590873453554983257010205964515397850605478418005567477856312542100090910917065614439415249650791715023353163873850777743785917243, 65537), 
# 		'google.com': [['ccabitter@gmail.com', 'gmailpassword'], ['cameron.bitter@berwickacademy.org', 'berwickpassword']],
# 		'amazon.com': [['ccabitter@gmail.com', 'amazonpassowrd', ]]
# 	}
# }   




