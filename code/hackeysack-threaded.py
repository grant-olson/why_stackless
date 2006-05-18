import thread
import random

class hackysacker:
    def __init__(self,name,circle):
        self.name = name
        self.circle = circle
        circle.append(self)
        self.messageQueue = []

        thread.start_new_thread(self.messageLoop,())

    def incrementCounter(self):
        hackysacker.counter += 1
        if hackysacker.counter >= 100000:
            sys.exit()

    def messageLoop(self):
        while 1:
            if self.messageQueue:
                message = self.messageQueue.pop()
                print "%s got hackeysack from %s" % (self.name, message.name)
                kickTo = self.circle[random.randint(0,len(self.circle)-1)]
                print "%s kicking hackeysack to %s" % (self.name, kickTo.name)
                self.incrementCounter()
                kickTo.messageQueue.append(self)
                

def runit():
    circle = []
    one = hackysacker('1',circle)

    for i in range(1000):
        hackysacker(`i`,circle)

    one.messageQueue.append(one)

    while 1:
        pass

