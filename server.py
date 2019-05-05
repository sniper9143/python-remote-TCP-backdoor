import socket
import sys
import os

class TCPserver:

    def __init__(self, host, port):
        self.sHost = host
        self.iPort = port
        self.cSocket = socket.socket()
        self.cClient = None
        self.sAddress = None

    def fConfigureSocket(self):
        self.cSocket.bind(('', self.iPort))
        self.cSocket.listen(5)

    def fSendSocket(self, command):
          self.cClient.send(command.encode())

    def fConnectionsManager(self):
        self.cClient, self.sAddress = self.cSocket.accept()
        if self.cClient != None and self.sAddress != None:
            return True

    @property
    def fListenClient(self):
        output = self.cClient.recv(99999).decode()
        if output != '400': return output
        else: return ''

    @property
    def fGetClientAddress(self):
        return self.sAddress

server = TCPserver('localhost', 8080)
server.fConfigureSocket()

print('TCP Server\n----------------------------------------\n')
print('Waiting for client connection...\n')

while True:
    if server.fConnectionsManager() == True:
        print('recieved connection from ' + str(server.fGetClientAddress[0]) + ':' + str(server.fGetClientAddress[1]) + '\n')
        break

while True:
    try:
        command = input(str(server.fGetClientAddress[0]) + ':' + str(server.fGetClientAddress[1]) + ' : input command: ')
        server.fSendSocket(command)
        print(server.fListenClient)
    except:
        pass
