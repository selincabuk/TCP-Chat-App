import atexit
import socket
import threading

class ChatServer:
    def __init__(self):
        self.users = {}
        self.addresses = {}
        self.user_messages = {}
        self.host = ""
        self.port = 25000
        self.socketFamily = socket.AF_INET
        self.socketType = socket.SOCK_STREAM
        self.serverSocket = socket.socket(self.socketFamily, self.socketType)

    def start(self):
        self.serverSocket.bind((self.host, self.port))
        self.serverSocket.listen()
        print("Chat server is up and running!")
        print("Listening for new connections on port {}.".format(self.port))

        connThread = threading.Thread(target=self.connectionThread)
        connThread.start()
        connThread.join()

    def connectionThread(self):
        while True:
            try:
                client, address = self.serverSocket.accept()
            except:
                print("Something went wrong while accepting incoming connections!")
                break
            print("{} has connected.".format(address[0]))
            self.addresses[client] = address
            threading.Thread(target=self.clientThread, args=(client,)).start()

    def clientThread(self, client):
        address = self.addresses[client][0]
        try:
            user = self.getNickname(client)
        except:
            print("Something went wrong while setting the nickname for {}!".format(address))
            self.closeConnection(client)
            return
        print("{} set its nickname to {}!".format(address, user))
        self.users[client] = user
        self.user_messages[user] = []
        self.broadcast("{} has joined the chat room!".format(user))

        while True:
            try:
                message = client.recv(2048).decode("utf8")
                if message == "/quit":
                    self.closeConnection(client)
                    break
                elif message == "/online":
                    self.sendOnlineUsers(client)
                elif message == "/commands":
                    self.sendCommands(client)
                elif message.startswith("/search "):
                    self.searchMessages(client, message)
                elif message == "/history":
                    self.sendHistory(client, user)
                else:
                    print("{} ({}): {}".format(address, user, message))
                    self.user_messages[user].append(message)
                    self.broadcast(message, user)
            except:
                self.closeConnection(client)
                break

    def getNickname(self, client):
        client.send("Welcome to Chat! Please type your nickname:".encode("utf8"))
        nickname = client.recv(2048).decode("utf8").strip()
        alreadyTaken = False
        if nickname in self.users.values():
            alreadyTaken = True
            while alreadyTaken:
                client.send("This nickname has already been taken. Please choose a different one:".encode("utf8"))
                nickname = client.recv(2048).decode("utf8").strip()
                if nickname not in self.users.values():
                    alreadyTaken = False
        return nickname

    def sendOnlineUsers(self, client):
        onlineUsers = ', '.join([user for user in sorted(self.users.values())])
        client.send("Users online are: {}".format(onlineUsers).encode("utf8"))

    def sendCommands(self, client):
        client.send("Available commands are /commands, /online, /quit, /history, /search".encode("utf8"))

    def searchMessages(self, client, message):
        keyword = message.split(" ", 1)[1]
        history = '\n'.join([msg for msg in self.user_messages[self.users[client]] if keyword in msg])
        client.send("Search results:\n{}".format(history).encode("utf8"))

    def sendHistory(self, client, user):
        history = '\n'.join(self.user_messages[user])
        client.send("Message history:\n{}".format(history).encode("utf8"))

    def broadcast(self, message, sentBy=""):
        try:
            if sentBy == "":
                for user in self.users:
                    user.send(message.encode("utf8"))
            else:
                for user in self.users:
                    user.send("{}: {}".format(sentBy, message).encode("utf8"))
        except:
            print("Something went wrong while broadcasting a message!")

    def closeConnection(self, client):
        address = self.addresses[client][0]
        user = self.users[client]
        del self.addresses[client]
        del self.users[client]
        client.close()
        print("{} ({}) has left.".format(address, user))
        self.broadcast("{} has left the chat.".format(user))

    def cleanup(self):
        if len(self.addresses) != 0:
            for sock in self.addresses.keys():
                sock.close()
        print("Cleanup done.")

def main():
    chatServer = ChatServer()
    atexit.register(chatServer.cleanup)
    chatServer.start()

if __name__ == "__main__":
    main()
