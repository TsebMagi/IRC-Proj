# Client files for CS494
# Doug Whitley Fall 2016

import Packets
import threading
import socketserver
import socket

# basic server connection set up
listening_host = '0.0.0.0'
listening_port = 9002
client_address = (listening_host, listening_port)

SERVER_ADDRESS = ("0.0.0.0", 9001)

# user name base value and queue for messages
USERNAME = "badUser"

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


class IRCClient(socketserver.StreamRequestHandler):

    def handle(self):
        try:
            # get data
            data = self.rfile.readline().strip()
            message = Packets.decode(data)

            if isinstance(message, Packets.Message):
                print(lineHeader + message.username + "-> " + message.room_to_message + " " + message.message)
            elif isinstance(message, Packets.Pm):
                print(lineHeader + message.sent_from + ": "+ message.message)
            elif isinstance(message, Packets.Disconnect):
                print("You have been disconnected")
                exit(1)
            else:
                print("Error Recieved Bad Packet")
        except SystemError:
            exit(1)


def user_input(username):
    while 1:
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender.connect(SERVER_ADDRESS)
        inpt = input(lineHeader + username + "> ")
        if inpt == "/quit":
            # disconnect
            to_server = Packets.Disconnect(username)
            try:
                sender.send(to_server.encode())
            except socket.error as e:
                if e.errno == 111:
                    print("Could not connect to Server")
            sender.close()
            running = False
            break

        elif inpt.find("/message") != -1:
            inpt.strip("/message").strip()
            to_send = inpt.split(' ')
            if len(to_send) < 3:
                print("Not a valid message command try '/message <room name> <message>")
            else:
                to_server = Packets.Message(username, to_send[1],' '.join(to_send[2:]))
                send_to_server(to_server)

        elif inpt.find("/create") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not a valid create command try '/create <room name>' ")
            else:
                to_server = Packets.CreateRoom(username, to_send[1])
                send_to_server(to_server)

        elif inpt.find("/join") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not valid join command try '/join <room name>'")
            else:
                to_server = Packets.CreateRoom(username, to_send[1])
                send_to_server(to_server)

        elif inpt.find("/list rooms") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not a valid list command try:  '/list rooms' ")
            else:
                to_server = Packets.ListRooms()
                send_to_server(to_server)

        elif inpt.find("/list users") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 3:
                print("Not a valid list command try '/list users <room name>'")
            else:
                to_server = Packets.ListMembers(to_send[2])
                send_to_server(to_server)

        elif inpt.find("/leave") != -1:
            to_send = inpt.split(' ')
            if len(to_send) != 2:
                print("Not valid leave command try '/leave <room name>'")
            else:
                to_server = Packets.LeaveRoom(username, to_send[1])
                send_to_server(to_server)

        elif inpt.find("/PM") != -1:
            to_send = inpt.split(' ')
            if len(to_send) < 3:
                print("Not a valid Pm command try '/PM <username> <message>'")
            else:
                to_server = Packets.Pm(username, to_send[1], ' '.join(to_send[2:]))
                send_to_server(to_server)

        elif inpt.find("/help") != -1:
            print(helpText)

        else:
            print(lineHeader + "> " + "Invalid Command type '/help' for a list of valid commands and their usage.")


def send_to_server(message: Packets.Packet):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(SERVER_ADDRESS)
        s.send(message.encode())
        error = Packets.decode(s.makefile("r").readline().strip())
        if error.errors != Packets.Errors.NO_ERROR:
            print("Error: " + error.errors.__str__())
        s.close()
    except socket.error as e:
        if e.errno == 111:  # connection error
            print("Could not connect to server")
        else:
            print(e)


if __name__ == '__main__':
    # setup user name
    USERNAME = input("Enter Username: ").strip()
    while USERNAME.find(' ') != -1:
        print("Invalid user name, no spaces allowed")
        USERNAME = input("Enter Username: ").strip()
    client = socketserver.ThreadingTCPServer((SERVER_ADDRESS[0],SERVER_ADDRESS[1]+1), IRCClient)
    client_thread = threading.Thread(target= client.serve_forever)
    client_thread.daemon = True
    client_thread.start()
    user_input(USERNAME)
