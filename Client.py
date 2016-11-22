# Client files for CS494
# Doug Whitley Fall 2016

import queue
import Packets
import threading
import socket

# basic server connection set up
host = '0.0.0.0'
port = 9001
server_address = (host, port)

# user name base value and queue for messages
USERNAME = "badUser"
messages = queue.Queue()

# used for enabling the testing output
testing = True

# used for stock output
helpText = """Available commands:
/quit (Quits the server)
/message <Room Name> <Message for Room>
/create <Room Name to Create>
/join <Room Name to Join>
/list rooms (Displays a list of the rooms on the server)
/list users <Room to see users from>
/leave <Room Name to Leave>
/PM <User Name to Message> <Message>
/help (displays this help message)"""

# used for stock output
lineHeader = "IRC Chat: "


def user_input(username):
    sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sender.connect(server_address)
    while 1:
        inpt = input(lineHeader + username + "> ")
        if inpt == "/quit":
            # disconnect
            to_server = Packets.Disconnect(username)
            if testing:
                print(to_server.encode())
            sender.send(to_server.encode())
            sender.close()
            break

        elif inpt.find("/message") != -1:
            inpt.strip("/message").strip()
            to_send = inpt.split(' ')
            if len(to_send) < 3:
                print("Not a valid message command try '/message <room name> <message>")
            else:
                to_server = Packets.Message(username, to_send[1],' '.join(to_send[2:]))
                if testing:
                    print(to_server.encode())
                # send to server
        elif inpt.find("/create") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not a valid create command try '/create <room name>' ")
            else:
                to_server = Packets.CreateRoom(username, to_send[1])
                if testing:
                    print(to_server.encode())
        elif inpt.find("/join") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not valid join command try '/join <room name>'")
            else:
                to_server = Packets.CreateRoom(username, to_send[1])
                if testing:
                    print(to_server.encode())

        elif inpt.find("/list rooms") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not a valid list command try:  '/list rooms' ")
            else:
                to_server = Packets.ListRooms()
                if testing:
                    print(to_server.encode())

        elif inpt.find("/list users") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 3:
                print("Not a valid list command try '/list users <room name>'")
            else:
                to_server = Packets.ListMembers(to_send[2])
                if testing:
                    print(to_server.encode())

        elif inpt.find("/leave") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not valid leave command try '/leave <room name>'")
            else:
                to_server = Packets.LeaveRoom(username, to_send[1])
                if testing:
                    print(to_server.encode())

        elif inpt.find("/PM") != -1:
            to_send = inpt.split(' ')
            if len(to_send) < 3:
                print("Not a valid Pm command try '/PM <username> <message>'")
            else:
                to_server = Packets.Pm(username, to_send[1], ' '.join(to_send[2:]))
                if testing:
                    print(to_server.encode())

        elif inpt.find("/help") != -1:
            print(helpText)

        else:
            print(lineHeader + "> " + "Invalid Command type '/help' for a list of valid commands and their usage.")


def server_input():
    # read from server
    print("working")


class IRCServer(object):

    if __name__ == '__main__':
        # setup user name
        USERNAME = input("Enter Username: ").strip()
        while USERNAME.find(' ') != -1:
            print("Invalid user name, no spaces allowed")
            USERNAME = input("Enter Username: ").strip()
        # connect to server
        if testing:
            to_server = Packets.Connect(USERNAME)
            packetString = to_server.encode()
            print(packetString)
        server_input = threading.Thread(target=server_input())
        server_input.daemon = True
        server_input.start()
        user_input(USERNAME)
