import thread
import random
import sys
import Queue

class hackysacker:
    counter = 0
    def __init__(self,name,circle):
        self.name = name
        self.circle = circle
        circle.append(self)
        self.messageQueue = Queue.Queue()

        thread.start_new_thread(self.messageLoop,())

    def incrementCounter(self):
        hackysacker.counter += 1
        if hackysacker.counter >= turns:
            while self.circle:
                self.circle.pop().messageQueue.put('exit')

    def messageLoop(self):
        while 1:
            message = self.messageQueue.get()
            if message == "exit":
                debugPrint("%s is going home" % self.name)
                sys.exit()
            debugPrint("%s got hackeysack from %s" % (self.name, message.name))
            kickTo = self.circle[random.randint(0,len(self.circle)-1)]
            debugPrint("%s kicking hackeysack to %s" % (self.name, kickTo.name))
            self.incrementCounter()
            kickTo.messageQueue.put(self)
                


def debugPrint(x):
    if debug:
        print x

def runit():
    hackysacker.counter= 0
    circle = []
    one = hackysacker('1',circle)

    for i in range(hackysackers):
        hackysacker(`i`,circle)

    one.messageQueue.put(one)

    while circle:
        pass


debug=0
hackysackers=10000
turns = 1000

