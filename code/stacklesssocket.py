#
# Stackless compatible socket module:
#
# This wraps the asyncore module and the dispatcher class it provides in order
# write a socket module replacement that uses channels to allow calls to it to
# block until a delayed event occurs.
#
# Not all aspects of the socket module are provided by this file.  Examples of
# it in use can be seen at the bottom of this file.
#
# NOTE: Versions of the asyncore module from Python 2.4 or later include bug
#       fixes and earlier versions will not guarantee correct behaviour.
#       Specifically, it monitors for errors on sockets where the version in
#       Python 2.3.3 does not.
#

# Possible improvements:
# - More correct error handling.  When there is an error on a socket found by
#   poll, there is no idea what it actually is.
# - Launching each bit of incoming data in its own tasklet on the readChannel
#   send is a little over the top.  It should be possible to add it to the
#   rest of the queued data

import stackless
import asyncore
import socket as stdsocket # We need the "socket" name for the function we export.

# If we are to masquerade as the socket module, we need to provide the constants.
for k, v in stdsocket.__dict__.iteritems():
    if k.upper() == k:
        locals()[k] = v
error = stdsocket.error

managerRunning = False

def ManageSockets():
    global managerRunning

    while len(asyncore.socket_map):
        # Check the sockets for activity.
        asyncore.poll(0.0)
        # Yield to give other tasklets a chance to be scheduled.
        stackless.schedule()

    managerRunning = False

def socket(family=AF_INET, type=SOCK_STREAM, proto=0):
    global managerRunning

    currentSocket = stdsocket.socket(family, type, proto)
    ret = dispatcher(currentSocket)
    # Ensure that the sockets actually work.
    if not managerRunning:
        managerRunning = True
        stackless.tasklet(ManageSockets)()
    return ret

class dispatcher(asyncore.dispatcher):
    def __init__(self, sock):
        # This is worth doing.  I was passing in an invalid socket which was
        # an instance of dispatcher and it was causing tasklet death.
        if not isinstance(sock, stdsocket.socket):
            raise StandardError("Invalid socket passed to dispatcher")
    
        asyncore.dispatcher.__init__(self, sock)

        self.acceptChannel = stackless.channel()
        self.connectChannel = stackless.channel()
        self.readChannel = stackless.channel()

        self.readBuffer = ''
        self.outBuffer = ''

    def writable(self):
        return (not self.connected) or len(self.outBuffer)

    def accept(self):
        return self.acceptChannel.receive()

    def connect(self, address):
        asyncore.dispatcher.connect(self, address)
        if not self.connected:
            self.connectChannel.receive()

    def send(self, data):
        self.outBuffer += data
        return len(data)

    # Read at most byteCount bytes.
    def recv(self, byteCount):
        if len(self.readBuffer) < byteCount:
            self.readBuffer += self.readChannel.receive()
        ret = self.readBuffer[:byteCount]
        self.readBuffer = self.readBuffer[byteCount:]
        return ret

    def close(self):
        asyncore.dispatcher.close(self)
        self.connected = False
        self.accepting = False

        # Clear out all the channels with relevant errors.
        while self.acceptChannel.balance < 0:
            self.acceptChannel.send_exception(error, 9, 'Bad file descriptor')
        while self.connectChannel.balance < 0:
            self.connectChannel.send_exception(error, 10061, 'Connection refused')
        while self.readChannel.balance < 0:
            self.readChannel.send_exception(error, 10054, 'Connection reset by peer')

    def handle_accept(self):
        if self.acceptChannel.balance < 0:
            currentSocket, clientAddress = asyncore.dispatcher.accept(self)
            currentSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            # Give them the asyncore based socket, not the standard one.
            currentSocket = self.wrap_accept_socket(currentSocket)
            stackless.tasklet(self.acceptChannel.send)((currentSocket, clientAddress))

    # Inform the blocked connect call that the connection has been made.
    def handle_connect(self):
        self.connectChannel.send(None)

    # Just close the socket.  That should send kind of relevant errors to waiting calls.
    def handle_close(self):
        self.close()

    # Some error, just close the channel and let that raise errors to blocked calls.
    def handle_expt(self):
        self.close()

    def handle_read(self):
        buf = asyncore.dispatcher.recv(self, 20000)
        stackless.tasklet(self.readChannel.send)(buf)

    def handle_write(self):
        if len(self.outBuffer):
            sentBytes = asyncore.dispatcher.send(self, self.outBuffer[:512])
            self.outBuffer = self.outBuffer[sentBytes:]

    # In order for incoming connections to be stackless compatible, they need to be
    # wrapped by an asyncore based dispatcher subclass.
    def wrap_accept_socket(self, currentSocket):
        return dispatcher(currentSocket)


if __name__ == '__main__':
    import struct
    # Test code goes here.
    testAddress = "127.0.0.1", 3000
    info = -12345678
    data = struct.pack("i", info)
    dataLength = len(data)

    print "creating listen socket"
    def ManageListener(address):
        global info, data, dataLength
    
        listenSocket = socket(AF_INET, SOCK_STREAM)
        listenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listenSocket.bind(address)
        listenSocket.listen(5)
        # We will have to manually close the listening socket, at which point it
        # should be the last one left and we want the socket manager tasklet to
        # exit then.

        NUM_TESTS = 2
        
        i = 1
        while i < NUM_TESTS + 1:
            # No need to schedule this tasklet as the accept should yield most
            # of the time on the underlying channel.
            print "waiting for connection test", i
            currentSocket, clientAddress = listenSocket.accept()
            print "received connection", i, "from", clientAddress
            
            if i == 1:
                currentSocket.close()
            elif i == 2:
                print "server test", i, "send"
                currentSocket.send(data)
                try:
                    print "server test", i, "recv"
                    currentSocket.recv(4)
                    break                    
                except error:
                    pass
            else:
                currentSocket.close()
            
            print "server test", i, "OK"
            i += 1

        if i != NUM_TESTS+1:
            print "server: FAIL", i
        else:
            print "server: OK", i

        listenSocket.close()

    def TestClientConnections(address):
        global info, data, dataLength
    
        # Attempt 1:
        clientSocket = socket()
        clientSocket.connect(address)
        print "client connection", 1, "waiting to recv"
        try:
            clientSocket.recv(5)
            print "client test", 1, "FAIL"
            return
        except error:
            pass
        print "client test", 1, "OK"

        # Attempt 2:
        clientSocket = socket()
        clientSocket.connect(address)
        print "client connection", 2, "waiting to recv"
        s = clientSocket.recv(dataLength)
        t = struct.unpack("i", s)
        if t[0] == info:
            print "client test", 2, "OK"
        else:
            print "client test", 2, "FAIL"
        clientSocket.close()

    stackless.tasklet(ManageListener)(testAddress)
    stackless.tasklet(TestClientConnections)(testAddress)
    stackless.run()
    print "result: SUCCESS"
