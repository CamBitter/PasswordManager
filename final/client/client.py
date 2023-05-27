from tkinter import *
from tkinter.simpledialog import askstring
from tkinter.scrolledtext import ScrolledText

import configparser
import threading
import rsa
import socket
import pickle
import sys
import time
import pyperclip


with open("keys/id_rsa.pub", "rb") as f:
    pubKey = pickle.load(f)

with open("keys/id_rsa", "rb") as f:
    privKey = pickle.load(f)

# read config from file
config = configparser.ConfigParser()
config.read("config.ini")


HEADER_LENGTH = int(config["CONFIG"]["HEADER_LENGTH"])
HOST = str(config["CONFIG"]["HOST"])
PORT = int(config["CONFIG"]["PORT"])


def makeMSG(msg):
    msg_header = f"{len(msg.encode()):<{HEADER_LENGTH}}".encode()
    return msg_header + msg.encode()

def getMSG(s):
	msg_header = s.recv(HEADER_LENGTH)
	msg_length = int(msg_header.decode().strip())
	msg = s.recv(msg_length)
	msg = decryptMSG(msg)
	return msg

def encryptMSG(msg):
    return rsa.encrypt(msg.encode(), pubKey)

def decryptMSG(msg):
    return rsa.decrypt(msg, privKey).decode()
 

class Client():
	def __init__(self, HOST, PORT):
		
		self.HEADER_LENGTH = 10
		self.close_connection = False

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((HOST, PORT))

		self.username = input("Username: ")
		self.s.send(makeMSG(self.username))
		

		msg = getMSG(self.s) #gets welcome message
		print(msg)

		msg = getMSG(self.s) #password request
		print(msg)
		if msg == "User not found in database, closing connection":
			print("Exiting program.")
			sys.exit()

		self.s.send(makeMSG(input(""))) #send password

		msg = getMSG(self.s) #get error or ok messge
		print(msg)
		if (msg == "INVALID PASS"):
			print("Exiting program.")
			sys.exit()


		thread = threading.Thread(target = self.main_loop)
		thread.daemon = True
		thread.start()

		self.gui_loop()


	def main_loop(self):

		# recvMSG function
		while True:
			noUpdate = False
			
			time.sleep(0.1)

			msg_header = self.s.recv(self.HEADER_LENGTH)
			msg_length = int(msg_header.decode().strip())
			msg = self.s.recv(msg_length)
			msg = decryptMSG(msg)

			if msg == "Terminating session . . . ":
				self.s.close()
				self.root.destroy()
				break

			elif "PASS-->:" in msg:
				print("pass incoming")
				msg = msg[8:]
				pyperclip.copy(msg)
				noUpdate = True

			if not noUpdate:
				msg += "\n"
				self.textBox.config(state = NORMAL)
				self.textBox.insert(END, msg)
				self.textBox.yview('end')
				self.textBox.config(state = DISABLED)


	def gui_loop(self):
		self.root = Tk()
		self.root.title("Password Manager")

		self.textBox = ScrolledText(self.root, height = '20', width = '80', bg = "lightgray")
		self.textBox.config(state = DISABLED, font = ("Arial", 12))
		self.textBox.pack(fill = BOTH, expand = YES)


		self.sendBtn = Button(self.root, text = "Send Message")
		self.sendBtn.pack(fill = BOTH, expand = YES)

		# self.enterText = Text(self.root, bg = "lightgray", height = 4, wrap = None)
		# self.enterText.pack(fill = BOTH, expand = YES)
		# self.enterText.bind("<Return>", lambda event: self.sendMSG())

		self.enterText = Entry(self.root, bg = "lightgray", font=('Arial', 16))
		self.enterText.pack(fill = BOTH, expand = YES)
		self.enterText.bind("<Return>", lambda event: self.sendMSG())

		self.sendBtn.configure(command = self.sendMSG)
		self.root.protocol("WM_DELETE_WINDOW", self.exit)
		self.root.mainloop()


	def sendMSG(self):
		text = self.enterText.get()
		text = text.strip()

		self.enterText.delete(0, END)

		if text == "":
			return
		
		elif text == "clear":
			self.textBox.config(state = NORMAL)
			self.textBox.delete('1.0', END)
			self.textBox.config(state = DISABLED)
			return

		self.s.send(makeMSG(text))


	def exit(self):
		self.close_connection = True
		time.sleep(1)
		self.root.destroy()


client = Client(HOST, PORT)




