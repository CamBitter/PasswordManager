from password_generator import PasswordGenerator
import dataEnc as encoder
import socket
import sys
import random
import pickle
import rsa
import pyperclip
import configparser


with open("keys/id_rsa.pub", "rb") as f:
    pubKey = pickle.load(f)

try:
    with open("data.dat", "rb") as f:
        serverData = encoder.decryptData(pickle.load(f))

except Exception as e:
    print("Data file corrupted, please run clean.py")


config = configparser.ConfigParser()
config.read("config.ini")

HEADER_LENGTH = int(config["CONFIG"]["HEADER_LENGTH"])
HOST = str(config["CONFIG"]["HOST"])
PORT = int(config["CONFIG"]["PORT"])

pyperclip.copy(PORT) 
print(f"Accepting connections on {HOST}:{PORT}")


def saveData():
    with open("data.dat", "wb") as f:
        encodedData = encoder.encryptData(serverData)
        pickle.dump(encodedData, f)


def getMSG(connection):
    try:
        msg_header = connection.recv(HEADER_LENGTH)

        if not len(msg_header):
            return {"data": ""}

        msg_length = int(msg_header.decode().strip())
        msg = connection.recv(msg_length)

        return {"header": msg_header, "data": msg.decode()}

    except Exception as e:
        print(e)
        return {"data": ""}

def makeMSG(msg):
    msg_header = f"{len(encryptMSG(msg)):<{HEADER_LENGTH}}"
    msg = msg_header.encode() + encryptMSG(msg)

    return msg


def encryptMSG(msg):
    return rsa.encrypt(msg.encode(), pubKey)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen()

    while True:

        conn, addr = s.accept()

        print(f"Attempting connection by {addr}")

        username = getMSG(conn)["data"] #gets username
        print(f"{username} logging in . . .")
        conn.send(makeMSG(f"Welcome, {username}")) #send welcome message

        continue0 = True

        if username in serverData: 
            conn.send(makeMSG("Enter Password: ")) 

            if getMSG(conn)["data"] == serverData[username]["PASS"]:
                print("Authenticated.")

                passwords = "\n"
                for website in serverData[username]:
                    if website != "PASS" and website != "PUBKEY":
                        passwords += website + "\n"
                        for login in serverData[username][website]:
                            passwords += f"        {login[0]}   —   {login[1]}\n"

                conn.send(makeMSG("Successfully logged into server."))

            else:
                conn.send(makeMSG("INVALID PASS"))
                continue0 = False

        else:
            conn.send(makeMSG("User not found in database, closing connection"))
            continue0 = False

        while continue0:
            response = getMSG(conn) 
            msg = response["data"]

            if not msg:
                print(f"No response from {addr}, closing connection")
                continue0 = False


            elif msg == "exit":
                conn.send(makeMSG("Terminating session . . . "))
                print(f"Connection closed by {addr} using 'exit'")
                continue0 = False


            elif msg == "list":
                num_urls = 0
                for url in serverData[username]:
                    if url != "PASS" and url != "PUBKEY":
                        num_urls += 1

                if num_urls > 0:
                    conn.send(makeMSG("——————————————"))

                    for url in serverData[username]:
                        if url != "PASS" and url != "PUBKEY":
                            conn.send(makeMSG(url))
                            for account in serverData[username][url]:
                                try:
                                    conn.send(makeMSG("    >" + account[0]))
                                    conn.send(makeMSG("         >" +(account[1])))
                                except IndexError as e:
                                    print("Index error exception on line 135 in -list command")

                    conn.send(makeMSG("——————————————"))

                else:
                    conn.send(makeMSG("No urls added, try -addkey"))


            elif msg == "addkey":
                try:
                    conn.send(makeMSG("Enter a name / url for this entry:"))
                    url = getMSG(conn)["data"].lower()
                    conn.send(makeMSG(f"What username would you like to add to {url}:"))
                    accname = getMSG(conn)["data"]

                    try:
                        x = serverData[username][url.lower()][0]
                    except KeyError:
                        serverData[username][url] = []
                    except IndexError:
                        pass


                    if ([a[0] for a in serverData[username][url.lower()]].count(accname) >= 1):
                        conn.send(makeMSG("Username already has a password, try again with a different account."))

                    else:
                        conn.send(makeMSG("How long should the autogenerated pass. be: "))
                        length = int(getMSG(conn)["data"])
                        conn.send(makeMSG("Use special characters !)@#$%^&( (Y/N, default is Y)"))
                        SP = getMSG(conn)["data"].lower()

                        SP = False if SP == "n" or SP == "no" else True
                        pg = PasswordGenerator()
                        if SP:
                            password = pg.shuffle_password("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&'()*+,-./:;<=>?@[^_`{|}~", length)
                        else:
                            password = pg.shuffle_password("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", length)

                        conn.send(makeMSG(f"Password generated, added as {accname} for {url} --> " + password))

                        try:
                            serverData[username][url].append([accname, password])
                        except:
                            serverData[username][url] = []
                            serverData[username][url].append([accname, password])

                        saveData()

                except Exception as e:
                    print(e)
                    conn.send(makeMSG("There was an error, please try again."))
                    

            elif msg == "rmkey":
                try:
                    conn.send(makeMSG("What url is the account under:"))
                    url = getMSG(conn)["data"]

                    if not url in serverData[username]:
                        conn.send(makeMSG("Invalid URL, please retry."))
                    else:
                        conn.send(makeMSG("Account name:"))
                        accname = getMSG(conn)['data']

                        if not (accname in [x[0] for x in serverData[username][url]]):
                            conn.send(makeMSG("Account name not found in url, please try again."))
       
                        else:
                            for i in range(len(serverData[username][url])):
                                try:
                                    if serverData[username][url][i][0] == accname:
                                        serverData[username][url].pop(i)
                                except IndexError as e:
                                    print(e)

                        if len(serverData[username][url]) == 0:
                            del serverData[username][url]

                        print(f"removed key for {username}")
                        conn.send(makeMSG("Done."))

                    saveData()

                except Exception as e:
                    conn.send(makeMSG("There was an error, please try again."))
                    print(e)


            elif msg == "addpin":
                try:

                    conn.send(makeMSG("Enter a name / url for this entry:"))
                    url = getMSG(conn)["data"]  
                    conn.send(makeMSG(f"What username would you like to add to {url}:"))
                    accname = getMSG(conn)["data"]

                    try:
                        x = serverData[username][url.lower()][0]
                    except KeyError:
                        serverData[username][url] = []
                    except IndexError:
                        pass

                    if ([a[0] for a in serverData[username][url.lower()]].count(accname) >= 1):
                        conn.send(makeMSG("Username already has a password, try again with a different account."))

                    else:
                        conn.send(makeMSG("How long should the autogenerated pass. be: "))
                        length = int(getMSG(conn)["data"])

                        pg = PasswordGenerator()
                        password = pg.shuffle_password("0123456789", length)

                        conn.send(makeMSG(f"Password generated, added as {accname} for {url} --> " + password))

                        try:
                            serverData[username][url.lower()].append([accname, password])
                        except:
                            serverData[username][url.lower()] = []
                            serverData[username][url.lower()].append([accname, password])

                        saveData()
                

                except Exception as e:
                    conn.send(makeMSG("There was an error, please try again."))
                    print(e)


            elif msg == "copy":
                
                try:
                    conn.send(makeMSG("What url is the account under:"))
                    url = getMSG(conn)["data"].lower()

                    if not url in serverData[username]:
                        conn.send(makeMSG("Invalid URL, please restart."))
                    else:
                        conn.send(makeMSG("Account name:"))
                        accname = getMSG(conn)['data']

                        if not (accname in [x[0] for x in serverData[username][url]]):
                            conn.send(makeMSG("Account name not found in url, please try again."))

                        else:
                            for i in range(0, len(serverData[username][url])):

                                if serverData[username][url][i][0] == accname:
                                    conn.send(makeMSG(f"PASS-->:" + serverData[username][url][i][1]))
                                    conn.send(makeMSG(f"Password for {url}: {accname} copied to clipboard."))


                except Exception as e:
                    conn.send(makeMSG("There was an error, please try again."))
                    print(e)


            elif msg == "help":
                conn.send(makeMSG("addkey : adds key to database\nrmkey : removes a key from the database\naddpin : custom key generator\nlist : shows all passwords\ncopy : copies password to clipboard\nexit : Exit the session\nclear : clears the window\n"))


            else:
                conn.send(makeMSG("Unknown command, try 'help'"))



