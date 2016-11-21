from enum import Enum

# basic packets


class OpCode(Enum):
    CONNECT = 1
    DISCONNECT = 2
    CREATE_ROOM = 3
    JOIN_ROOM = 4
    LIST_ROOMS = 5
    LEAVE_ROOM = 6
    LIST_MEMBERS = 7
    PM = 8


class Status(Enum):
    OK = 0
    ERROR = 1


class Errors(Enum):
    NO_ERROR = 0
    SERVER_NOT_FOUND = 1
    ROOM_NOT_FOUND = 2
    USER_NOT_FOUND = 3


class Packet(object):

    def __init__(self, op_code, status=Status.OK, errors=Errors.NO_ERROR):
        self.op_code = op_code
        self.status = status
        self.errors = errors


class Connect (Packet):

    def __init__(self, username, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.CONNECT, status, errors)
        self.username = username


class Disconnect(Packet):

    def __init__(self, username, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.DISCONNECT, status, errors)
        self.username = username


class CreateRoom (Packet):

    def __init__(self, username, room, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.CREATE_ROOM, status, errors)
        self.username = username
        self.room = room


class JoinRoom (Packet):

    def __init__(self, username, room, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.JOIN_ROOM, status, errors)
        self.username = username
        self.room = room


class ListRooms(Packet):

    def __init__(self, response=None, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.LIST_ROOMS, status, errors)
        self.response = response


class LeaveRoom(Packet):

    def __init__(self, username, room, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.LEAVE_ROOM, status, errors)
        self.username = username
        self.room = room


class ListMembers(Packet):

    def __init__(self, room, response=None, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.LIST_MEMBERS, status, errors)
        self.room = room
        self.response = response


class Pm(Packet):

    def __init__(self, sent_from, sent_to, message, status=Status.OK, errors=Errors.NO_ERROR):
        super().__init__(OpCode.PM, status, errors)
        self.sent_from = sent_from
        self.sent_to = sent_to
        self.message = message