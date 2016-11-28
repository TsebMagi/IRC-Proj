# Server file for CS494
# Doug Whitley Fall 2016
import socket
import Packets
import socketserver
import sys


class Disconnection(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class User(object):
    def __init__(self, handle: str, address):
        self.handle = handle
        self.address = address


class Room(object):
    def __init__(self, room_name: str, users: User=None):
        if users is None:
            self.users = []
        else:
            self.users.append(users)
        self.room_name = room_name

    def add_to_room(self, user):
        self.users.append(user)


# list of users on the server
USERS = []
# list of Rooms on the server
ROOMS = []
# used for testing, in a normal distribution of this it would be run across networks
SERVER_ADDRESS = ('0.0.0.0', 9001)
SERVER_SOCKET = None


def interrupt_handler(signal, frame):
    SERVER_SOCKET.close()
    sys.exit(0)


class IRCServer(socketserver.StreamRequestHandler):


    @staticmethod
    def connect_process(packet: Packets.Connect, received_from: User) -> Packets.Errors:
        for user in USERS:
            if user.handle == packet.username:
                return Packets.Errors.USER_ALREADY_EXISTS
        USERS.append(User(packet.username,received_from))
        return Packets.Errors.NO_ERROR

    @staticmethod
    def disconnect_process(packet: Packets.Disconnect) -> Packets.Errors:
        for user in USERS:
            if user.handle == packet.username:
                USERS.remove(packet.username)
                return Packets.Errors.NO_ERROR
        return Packets.Errors.USER_NOT_FOUND

    @staticmethod
    def create_room_process(packet: Packets.CreateRoom) -> Packets.Packet:
        for room in ROOMS:
            if room.room_name == packet.room:
                return Packets.Errors.ROOM_ALREADY_EXISTS
        ROOMS.append(Room(packet.room, packet.username))
        return Packets.Errors.NO_ERROR

    @staticmethod
    def join_room_process(packet: Packets.JoinRoom) ->Packets.Errors:
        for room in ROOMS:
            if room.room_name == packet.room:
                room.add_to_room(packet.username)
                return Packets.Errors.NO_ERROR
        ROOMS.append(Room(packet.room, packet.username))
        return Packets.Errors.NO_ERROR

    @staticmethod
    def leave_room_process(packet: Packets.LeaveRoom) ->Packets.Errors:
        for room in ROOMS:
            for user in room.users:
                if user.handle == packet.username:
                    room.remove(user.handle)
                    return Packets.Errors.NO_ERROR
        return Packets.Errors.USER_NOT_IN_ROOM

    @staticmethod
    def list_rooms_process(packet: Packets.ListRooms) -> Packets.ListRooms:
        packet.response = ROOMS.__str__()
        return packet

    @staticmethod
    def list_members(packet: Packets.ListMembers) -> Packets.ListMembers:
        for room in ROOMS:
            if room.room_name == packet.room:
                packet.response = room.users.__str__()
                return packet
        packet.errors = Packets.Errors.ROOM_NOT_FOUND
        return packet

    @staticmethod
    def message_process(self, packet: Packets.Message) -> Packets.Message:
        for room in ROOMS:
            if room.room_name == packet.room_to_message:
                for user in room:
                    self.send_packet(packet, user)
                return packet
        packet.errors = Packets.Errors.ROOM_NOT_FOUND
        return packet

    @staticmethod
    def pm_process(self, packet: Packets.Pm) -> Packets.Message:
        for user in USERS:
            if user.handle == packet.sent_to:
                self.send_packet(packet,user)
                return packet
        packet.errors = Packets.Errors.USER_NOT_FOUND
        return packet

    @staticmethod
    def send_packet(packet: Packets.Packet, user):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(user.address)
            s.send(packet.decode())
            s.close()
        except socket.error as e:
            if e.errno == 111: #connection error
                USERS.remove(user)
            else:
                print(e)

    def handle(self):
        # get the input
        self.data = self.rfile.readline().strip()
        new_message = Packets.encode(self.data)
        # process the input
        try:
            # check for what type of packet was sent and process appropriately
            if isinstance(new_message, Packets.Connect):
                new_message.errors = self.connect_process(new_message,User(new_message.username, address))
            elif isinstance(new_message, Packets.Disconnect):
                new_message.errors = self.disconnect_process(new_message)
            elif isinstance(new_message, Packets.CreateRoom):
                new_message.errors = self.create_room_process(new_message)
            elif isinstance(new_message,Packets.JoinRoom):
                new_message.errors = self.join_room_process(new_message)
            elif isinstance(new_message, Packets.LeaveRoom):
                new_message.errors = self.leave_room_process(new_message)
            elif isinstance(new_message, Packets.Message):
                new_message.errors = self.message_process(new_message)
            elif isinstance(new_message, Packets.Pm):
                new_message.errors = self.pm_process(new_message)
            elif isinstance(new_message, Packets.ListMembers):
                new_message = self.list_members(new_message)
            elif isinstance(new_message, Packets.ListRooms):
                new_message = self.list_rooms_process(new_message)
            else:
                new_message.errors = Packets.Errors.MALFORMED_PACKET
        # handle any type errors
        except TypeError as e:
            new_message.errors = Packets.Errors.MALFORMED_PACKET
        self.wfile.write(new_message.decode())


if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(SERVER_ADDRESS,IRCServer)
    SERVER_SOCKET = server.socket
    server.serve_forever()
