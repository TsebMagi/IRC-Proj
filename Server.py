# Server file for CS494
# Doug Whitley Fall 2016
import socket
import queue
import threading
import Packets

USERS = []
ROOMS = []

testing = True

port = 9001
host = '0.0.0.0'
server_address = (host, port)
back_log = 5

class User(object):
    def __init__(self, handle, client, address):
        self.handle = handle
        self.client = client
        self.addres = address

class Message (object):
    def __init__(self, message, recipient):
        self.message = message
        self.recipient = recipient

messages_in = queue.Queue()
messages_out = queue.Queue()


def send_messages():
    if testing:
        print("sender is up")


def recieve_messages():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(server_address)
    listener.listen(back_log)
    if testing:
        print("receiver is up")
    while 1:
        client, address = listener.accept()
        new_connection = client.recv(2048)
        new_connection = Packets.decode(new_connection)
        print(new_connection)
        if new_connection:
            client.send(new_connection.encode())
            print("new connection from " + new_connection.encode())
        client.close()


class IRCServer(object):
    if __name__ == "__main__":

        sender = threading.Thread(target=send_messages())
        sender.daemon = True
        sender.start()
        recieve_messages()