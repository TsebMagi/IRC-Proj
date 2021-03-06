# Server file for CS494
# Doug Whitley Fall 2016
import socket
import Packets
import socketserver
import sys
import signal

testing = True


class User(object):
    def __init__(self, handle, address):
        self.handle = handle
        self.address = address


class Room(object):
    def __init__(self, room_name, users=None):
        if users is None:
            self.users = []
        else:
            self.users = [users]
        self.room_name = room_name

    def add_to_room(self, user):
        self.users.append(user)

    def __str__(self):
        return self.room_name

    def in_room(self,username):
        for user in self.users:
            if user == username:
                return True
        return False

    def remove_user(self,username):
        for user in self.users:
            if user == username:
                self.users.remove(user)
                return True
        return False


# list of users on the server
USERS = []
# list of Rooms on the server
ROOMS = []
# used for testing, in a normal distribution of this it would be run across networks
SERVER_ADDRESS = ("127.0.0.1", 9001)
SERVER_SOCKET = None


# The following handles a ctrl-c form the command line running the server
def interrupt_handler(signal, frame):
    SERVER_SOCKET.close()
    for user in USERS:
        IRCServer.send_packet(Packets.Disconnect, user)
    sys.exit(0)

signal.signal(signal.SIGINT, interrupt_handler)


class IRCServer(socketserver.StreamRequestHandler):

    @staticmethod
    def connect_process(packet, received_from):
        for user in USERS:
            if user[0] == packet.username:
                packet.status = Packets.Status.ERROR
                packet.errors = Packets.Errors.USER_ALREADY_EXISTS
                return packet
        USERS.append((packet.username, received_from[1]))
        if testing:
            print("Users: " + USERS.__str__())
        packet.status = Packets.Status.OK
        packet.errors = Packets.Errors.NO_ERROR
        return packet

    @staticmethod
    def disconnect_process(packet):
        for user in USERS:
            if user[0] == packet.username:
                USERS.remove(user)
                for room in ROOMS:
                    room.remove_user(packet.username)
                packet.status = Packets.Status.OK
                packet.errors = Packets.Errors.NO_ERROR
                return packet
        packet.status = Packets.Status.ERROR
        packet.errors = Packets.Errors.USER_NOT_FOUND
        return packet

    @staticmethod
    def create_room_process(packet):
        for room in ROOMS:
            if room.room_name == packet.room:
                packet.errors =  Packets.Status.ERROR
                packet.errors =  Packets.Errors.ROOM_ALREADY_EXISTS
                return packet
        ROOMS.append(Room(packet.room, packet.username))
        if testing:
            room_string = ""
            for room in ROOMS:
                room_string += room.room_name + room.users.__str__()
            print("Rooms: " + room_string)
        packet.status = Packets.Status.OK
        packet.errors = Packets.Errors.NO_ERROR
        return packet

    @staticmethod
    def join_room_process(packet):
        for room in ROOMS:
            if room.room_name == packet.room:
                room.add_to_room(packet.username)
                packet.status = Packets.Status.OK
                packet.errors = Packets.Errors.NO_ERROR
                return packet
        ROOMS.append(Room(packet.room, packet.username))
        if testing:
            room_string = ""
            for room in ROOMS:
                room_string += room.room_name + room.users.__str__()
            print("Rooms: " + room_string)
        packet.status = Packets.Status.OK
        packet.errors = Packets.Errors.NO_ERROR
        return packet

    @staticmethod
    def leave_room_process(packet):
        for room in ROOMS:
            if room.room_name == packet.room:
                room.remove_user(packet.username)
                packet.status = Packets.Status.OK
                packet.errors = Packets.Errors.NO_ERROR
                return packet
        packet.status = Packets.Status.ERROR
        packet.errors = Packets.Errors.USER_NOT_IN_ROOM
        return packet

    @staticmethod
    def list_rooms_process(packet):
        for room in ROOMS:
            packet.response += (room.room_name + ":")
        return packet

    @staticmethod
    def list_members(packet):
        for room in ROOMS:
            if room.room_name == packet.room:
                for user in room.users:
                    packet.response += (user + ":")
                return packet
        packet.status = Packets.Status.ERROR
        packet.errors = Packets.Errors.ROOM_NOT_FOUND
        return packet

    @staticmethod
    def message_process(self, packet):
        for room in ROOMS:
            if packet.room_to_message == room.room_name:
                for user in USERS:
                    if room.in_room(user[0]):
                        self.send_packet(packet, user)
                return packet
        packet.status = Packets.Status.ERROR
        packet.errors = Packets.Errors.ROOM_NOT_FOUND
        return packet

    @staticmethod
    def pm_process(self, packet):
        for user in USERS:
            if (user[0]) == packet.sent_to:
                self.send_packet(packet, user)
                return packet
        packet.status = Packets.Status.ERROR
        packet.errors = Packets.Errors.USER_NOT_FOUND
        return packet

    @staticmethod
    def send_packet(packet, user):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_ADDRESS[0], SERVER_ADDRESS[1]+100))
            s.send(packet.encode())
            s.close()
        except socket.error as e:
            if e.errno == 111:  # connection error
                if user in USERS:
                    USERS.remove(user)
            else:
                print(e)

    def broadcast_process(self, packet):
        for user in USERS:
            self.send_packet(packet, user)
        return packet

    def handle(self):
        # get the input
        new_input = self.rfile.readline()
        new_input = new_input.decode()
        new_input = new_input.strip()
        if testing:
            print("Server received Packet: " + new_input)
        address = self.connection.getpeername()
        try:
            new_message = Packets.decode(new_input)
        except TypeError as e:
            print("Error Processing received Packet: " + new_input + "error generated: " + e.__str__())
            return
        # process the input
        try:
            # check for what type of packet was sent and process appropriately
            if isinstance(new_message, Packets.Connect):
                new_message = self.connect_process(new_message, (new_message.username, address))
            elif isinstance(new_message, Packets.Disconnect):
                new_message = self.disconnect_process(new_message)
            elif isinstance(new_message, Packets.CreateRoom):
                new_message = self.create_room_process(new_message)
            elif isinstance(new_message,Packets.JoinRoom):
                new_message = self.join_room_process(new_message)
            elif isinstance(new_message, Packets.LeaveRoom):
                new_messagev= self.leave_room_process(new_message)
            elif isinstance(new_message, Packets.Message):
                new_message = self.message_process(self, new_message)
            elif isinstance(new_message, Packets.Pm):
                new_message = self.pm_process(self, new_message)
            elif isinstance(new_message, Packets.ListMembers):
                new_message = self.list_members(new_message)
            elif isinstance(new_message, Packets.Broadcast):
                new_message = self.broadcast_process(new_message)
            elif isinstance(new_message, Packets.ListRooms):
                new_message = self.list_rooms_process(new_message)
            else:
                new_message.status, new_message.errors = Packets.Status.ERROR, Packets.Errors.MALFORMED_PACKET
        # handle any type errors
        except TypeError as e:
            new_message.status, new_message.errors = Packets.Status.ERROR, Packets.Errors.MALFORMED_PACKET
            if testing:
                print ("Type Error in server handler: " + e.__str__())
        self.wfile.write(new_message.encode())
        return


if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(SERVER_ADDRESS,IRCServer)
    SERVER_SOCKET = server.socket
    server.serve_forever()
