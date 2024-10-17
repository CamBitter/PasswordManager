# PasswordManager

**Setup instructions:**

1. Download as a zip file
2. Extract zip file
3. Install Python3
4. Enter the directory and run `pip3 install -r requirements.txt`
5. For first time use, run `python3 clean.py` and follow instructions to setup a username and password
6. Leave IP address and header length blank, for Port enter any numbers between 50000-65000
7. Run `python3 server.py` in one window, then run `python3 client.py` in another to use the program

Here's an example setup for a server hosted on localhost on port 25560, with a client connected with the GUI terminal open.
The bottom windows show the data file which is encrypted using a Python RSA library using pub / priv key pairs.

<img width="1369" alt="Screenshot 2024-10-16 at 7 03 04 PM" src="https://github.com/user-attachments/assets/d6050986-9766-497d-a919-06938417e8d7">


