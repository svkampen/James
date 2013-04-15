"""
Some Extremely Crappy Socketry - secs.py
by Sam van Kampen, 2012
"""

import socket

def get_socket(address):
    sock = socket.socket()
    sock.connect(address)
    return sock

def send_data(sock, data, newline='\r\n'):
    try:
        print(data.rstrip())
        sock.send(data+newline)
    except Exception as e:
        print(e)

def get_data(sock, sbytes=1024):
    try:
        return sock.recv(sbytes)
    except Exception as e:
        print(e)
