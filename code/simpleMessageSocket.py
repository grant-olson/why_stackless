import stackless
from stacklesssocket import *

def defaultMessageAction(msg):
    print "Received Message " ,msg

def getMessages(server,port, act=defaultMessageAction):
    listenSocket = socket(AF_INET, SOCK_STREAM)
    listenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listenSocket.bind((server,port))
    listenSocket.listen(5)
    while 1:
        currentSocket, clientAddress = listenSocket.accept()
        stackless.tasklet(processMessage)(currentSocket, clientAddress,act)
        stackless.schedule()

def processMessage(sock,clientAddr,act=defaultMessageAction):
    msg = ""
    while 1:
        rec = sock.recv(32)
        import sys
        msg += rec
        if msg.endswith("\r\n\r\n"): break
        stackless.schedule()
    
    sock.send("OK\r\n\r\n")
    #sock.close()
    act(msg[:-4]) # strip newline and dispatch

def sendMessage(server,port,msg):
    sock = socket()
    sock.connect((server,port))
    sock.send(msg +"\r\n\r\n")
    msg = ""
    while 1:
        rec = sock.recv(32)
        import sys
        msg += rec
        if msg.endswith("\r\n\r\n"): break
        stackless.schedule()
    sock.close()
    if msg=="OK\r\n\r\n":
        pass
    else:
        print "Got bad response"

if __name__ == "__main__":
    stackless.tasklet(getMessages)("127.0.0.1",3000)
    stackless.tasklet(sendMessage)( "127.0.0.1",3000,"this is a test")
    stackless.run()