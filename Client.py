import queue
import Packets

# basic server connection set up
hostServer = '0.0.0.0'
portServer = 9001

# user name base value and queue for messages
USERNAME = "badUser"
messages = queue.Queue()

# used for enabling the testing output
testing = True

helpText = """Available commands:
/quit (Quits the server)
/message <Room Name> <Message for Room>
/create <Room Name to Create>
/join <Room Name to Join>
/list (Displays a list of the rooms on the server)
/list users <Room to see users from>
/leave <Room Name to Leave>
/PM <User Name to Message> <Message>
/help (displays this help message)"""

lineHeader = "IRC Chat: "


class IRCServer(object):

    if __name__ == '__main__':
        # setup user name
        USERNAME = input("Enter Username: ")

        while 1:
            inpt = input(lineHeader + USERNAME + "> ")
            if inpt == "/quit":
                # disconnect
                break
            elif inpt.find("/message") != -1:
                inpt.strip("/message").strip()
                break
            elif inpt.find("/create") != -1:
                inpt.strip("/create").strip()
            elif inpt.find("/join") != -1:
                inpt.strip("/join").strip()
            elif inpt.find("/list") != -1:
                inpt.strip("/list").strip()
            elif inpt.find("/list users") != -1:
                inpt.strip("/list users").strip()
            elif inpt.find("/leave") != -1:
                inpt.strip("/leave").strip()
            elif inpt.find("/PM") != -1:
                inpt.strip("/PM").strip()
            elif inpt.find("/help") != -1:
                print(helpText)
            else:
                print(lineHeader + "> " + "Invalid Command type '/help' for alist of valid commands and their usage.")