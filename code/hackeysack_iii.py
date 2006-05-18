import stackless
import random
import sys


class circle:
    def __init__(self):
        self.channel = stackless.channel()
        self.actors = []
        stackless.tasklet(self.messageLoop)()
        
    def messageLoop(self):
        while 1:
            msg = self.channel.receive()
            if msg == 'exit':
                return
            elif msg[1] == 'JOINS':
                debugPrint("ADDING PLAYER " , msg[0])
                self.actors.append(msg[0])
            elif msg[1] == "THROW":
                kickTo = self.actors[random.randint(0,len(self.actors)-1)]
                kickTo.send((self.channel, "BALL", "CIRCLE"))
            elif msg[1] == "ACTORS":
                msg[0].send( self.actors[:])
            else:
                print "UNKNOWN MESSAGE", msg
                
class hackysacker:
    counter = 0
    def __init__(self,name,circle):
        self.name = name
        self.circle = circle
        
        self.channel = stackless.channel()
        circle.send( (self.channel, 'JOINS'))

        stackless.tasklet(self.messageLoop)()

    def incrementCounter(self):
        hackysacker.counter += 1
        if hackysacker.counter >= turns:
            while self.circle:
                self.circle.send('exit')

    def messageLoop(self):
        while 1:
            message = self.channel.receive()
            debugPrint(message)
            if message == 'exit':
                return
            elif message[1] == "BALL":
                debugPrint("GOT HACKEYSACK")
                self.circle.send((self.channel, "ACTORS"))
                actors = self.channel.receive()
            
                kickTo = actors[random.randint(0,len(actors)-1)]
                while kickTo is self.channel:
                    kickTo = actors[random.randint(0,len(actors)-1)]
                debugPrint("%s kicking hackeysack to %s" % (self, kickTo))
                self.incrementCounter()
                kickTo.send((self.channel, "BALL", self.name))
            else:
                print "UNKNOWN MESSAGE" , message
                


def debugPrint(*x):
    if debug:print x
    
def runit():
    hackysacker.counter = 0
    c = circle()

    for i in range(hackysackers):
        hackysacker(`i`,c.channel)

    c.channel.send((c.channel, "THROW"))

    try:
        stackless.run()
    except TaskletExit:
        pass
    

debug = 0
hackysackers = 1000
turns = 10000

if __name__ == "__main__":
    runit()

    
