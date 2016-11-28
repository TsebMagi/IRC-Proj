# Packet class file for CS494
# Doug Whitley Fall 2016

from enum import Enum


# Allowed Op Codes
class OpCode(Enum):
    CONNECT = 1
    DISCONNECT = 2
    CREATE_ROOM = 3
    JOIN_ROOM = 4
    LEAVE_ROOM = 5
    LIST_ROOMS = 6
    LIST_MEMBERS = 7
    MESSAGE = 8
    PM = 9

    def __str__(self):
        return self.name


# Allowed Statuses
class Status(Enum):
    OK = 0
    ERROR = 1

    def __str__(self):
        return self.name

    @staticmethod
    def string_to_status(to_convert):
        if to_convert == "OK":
            return Status.OK
        elif to_convert == "ERROR":
            return Status.ERROR
        else:
            return None


# Allowed Errors
class Errors(Enum):
    NO_ERROR = 0
    SERVER_NOT_FOUND = 1
    ROOM_NOT_FOUND = 2
    ROOM_ALREADY_EXISTS = 3
    USER_NOT_FOUND = 4
    USER_ALREADY_EXISTS = 5
    USER_NOT_IN_ROOM = 6
    MALFORMED_PACKET = 7

    def __str__(self):
        return self.name

    @staticmethod
    def string_to_error(to_convert):
        if to_convert == "NO_ERROR":
            return Errors.NO_ERROR
        elif to_convert == "SERVER_NOT_FOUND":
            return Errors.SERVER_NOT_FOUND
        elif to_convert == "ROOM_NOT_FOUND":
            return Errors.ROOM_NOT_FOUND
        elif to_convert == "USER_NOT_FOUND":
            return Errors.USER_NOT_FOUND
        else:
            return None


class Packet(object):

    def __init__(self, op_code, status=Status.OK, errors=Errors.NO_ERROR):
        self.op_code = op_code
        self.status = status
        self.errors = errors

    def encode(self):
        return (self.op_code.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class Connect (Packet):

    def __init__(self, username, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.CONNECT, status, errors)
        self.username = username

    def encode(self):
        return (self.op_code.__str__()+" "+self.username.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class Disconnect(Packet):

    def __init__(self, username, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.DISCONNECT, status, errors)
        self.username = username

    def encode(self):
        return (self.op_code.__str__()+" "+self.username.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+'\n').encode()


class CreateRoom (Packet):

    def __init__(self, username, room, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.CREATE_ROOM, status, errors)
        self.username = username
        self.room = room

    def encode(self):
        return (self.op_code.__str__()+" "+self.username.__str__()+" "+self.room.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class JoinRoom (Packet):

    def __init__(self, username, room, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.JOIN_ROOM, status, errors)
        self.username = username
        self.room = room

    def encode(self):
        return (self.op_code.__str__()+" "+self.username.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class ListRooms(Packet):

    def __init__(self, response=None, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.LIST_ROOMS, status, errors)
        self.response = response

    def encode(self) -> str:
        return (self.op_code.__str__()+" "+self.response.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class LeaveRoom(Packet):

    def __init__(self, username, room, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.LEAVE_ROOM, status, errors)
        self.username = username
        self.room = room

    def encode(self):
        return (self.op_code.__str__()+" "+self.username.__str__()+" "+self.room.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class ListMembers(Packet):

    def __init__(self, room, response=None, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.LIST_MEMBERS, status, errors)
        self.room = room
        self.response = response

    def encode(self):
        return (self.op_code.__str__()+" "+self.room.__str__()+" "+self.response.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class Pm(Packet):

    def __init__(self, sent_from, sent_to, message, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.PM, status, errors)
        self.sent_from = sent_from
        self.sent_to = sent_to
        self.message = message

    def encode(self):
        return (self.op_code.__str__()+" "+self.sent_from.__str__()+" "+self.sent_to.__str__()+" "+self.message.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


class Message(Packet):

    def __init__(self, username, room_to_message, message, status=Status.OK,errors=Errors.NO_ERROR):
        super().__init__(OpCode.MESSAGE, status, errors)
        self.username = username
        self.room_to_message = room_to_message
        self.message = message

    def encode(self):
        return (self.op_code.__str__()+" "+self.username.__str__()+" "+self.room_to_message.__str__()+" "+self.message.__str__()+" "+self.status.__str__()+" "+self.errors.__str__()+"\n").encode()


def decode(packet_arg):
    split_packet = packet_arg.decode().split(" ")

    if split_packet[0] == "CONNECT":
        return Connect(split_packet[1], Status.string_to_status(split_packet[2]), Errors.string_to_error(split_packet[3]))
    elif split_packet[0] == "DISCONNECT":
        return Disconnect(split_packet[1], Status.string_to_status(split_packet[-2]), Errors.string_to_error(split_packet[-1]))
    elif split_packet[0] == "CREATE_ROOM":
        return CreateRoom(split_packet[1], split_packet[2], Status.string_to_status(split_packet[-2]), Errors.string_to_error(split_packet[-1]))
    elif split_packet[0] == "JOIN_ROOM":
        return JoinRoom(split_packet[1], split_packet[2], split_packet[-2], split_packet[-1])
    elif split_packet[0] == "LIST_ROOMS":
        return ListRooms(' '.join(split_packet[1:-2]), split_packet[-2], split_packet[-1])
    elif split_packet[0] == "LEAVE_ROOM":
        return LeaveRoom(split_packet[1], split_packet[-2], split_packet[-1])
    elif split_packet[0] == "LIST_MEMBERS":
        return ListMembers(split_packet[1], ' '.join(split_packet[2:-2]), split_packet[-2], split_packet[-1])
    elif split_packet[0] == "PM":
        return Pm(split_packet[1], split_packet[2], ' '.join(split_packet[3:-2]), split_packet[-2], split_packet[-1])
    elif split_packet[0] == "MESSAGE":
        return Message(split_packet[1], split_packet[2], ' '.join(split_packet[3:-2]), split_packet[-2], split_packet[-1])
    else:
        raise TypeError