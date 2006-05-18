import thread

class Ping:
    def __init__(self):
        self.channel = []
        self.done = 0

    def __call__(self):
        i = 100
        while i >= 0:
            if self.channel:
                print "Ping!"
                i -= 1
                a = self.channel.pop()
                a.channel.append(self)
        print "Ping Done!"
        self.done = 1

class Pong:
    def __init__(self):
        self.channel = []
        self.done = 0

    def __call__(self):
        i = 100
        while i >= 0:
            if self.channel:
                print "Pong!"
                i -= 1
                a = self.channel.pop()
                a.channel.append(self)
        print "Pong Done!"
        self.done = 1

    def initialize(self, other):
        other.channel.append(self)
        self()

ping = Ping()
pong = Pong()

thread.start_new_thread(ping,())
thread.start_new_thread(pong.initialize, (ping,))

while not ping.done or not pong.done:
    pass
