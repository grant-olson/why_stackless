import stackless
import random
import sys

class hackysacker:
    counter = 0
    def __init__(self,name,circle):
        self.name = name
        self.circle = circle
        circle.append(self)
        self.channel = stackless.channel()

        stackless.tasklet(self.messageLoop)()

    def incrementCounter(self):
        hackysacker.counter += 1
        if hackysacker.counter >= turns:
            while self.circle:
                self.circle.pop().channel.send('exit')

    def messageLoop(self):
        while 1:
            message = self.channel.receive()
            if message == 'exit':
                return
            debugPrint("%s got hackeysack from %s" % (self.name, message.name))
            kickTo = self.circle[random.randint(0,len(self.circle)-1)]
            while kickTo is self:
                kickTo = self.circle[random.randint(0,len(self.circle)-1)]
            debugPrint("%s kicking hackeysack to %s" % (self.name, kickTo.name))
            self.incrementCounter()
            kickTo.channel.send(self)
                


def debugPrint(x):
    if debug:print x

debug = 5
hackysackers = 5
turns = 1

def runit(hs=5,ts=5,dbg=1):
    global hackysackers,turns,debug
    hackysackers = hs
    turns = ts
    debug = dbg
    
    hackysacker.counter = 0
    circle = []
    one = hackysacker('1',circle)

    for i in range(hackysackers):
        hackysacker(`i`,circle)

    one.channel.send(one)

    try:
        stackless.run()
    except TaskletExit:
        pass
    

if __name__ == "__main__":
    runit()




