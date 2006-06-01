import stackless

class Listener:
    def __init__(self):
        self.channel = stackless.channel()
        stackless.tasklet(self.listen)()

    def listen(self):
        while 1:
            val = self.channel.receive()
            self.processMessage(val)

    def processMessage(self,val):
        pass
    
    def __call__(self,val):
        self.channel.send(val)

class Input(Listener):
    def __init__(self,name,reportTo,initialState=0):
        Listener.__init__(self)
        self.name = name
        self.reportTo = reportTo
        self.state = initialState

    def processMessage(self,val):
        self.state = val
        print "Set" , self,"to",self.state
        self.reportTo((self.name,self.state))

class Inverter(Listener):
    def __init__(self,outputs=None):
        Listener.__init__(self)
        self.inputA = Input('inputA',self)
        self.state = 0
        if outputs:
            self.outputs = outputs
        else:
            self.outputs = []
        

    def processMessage(self,msg):
        print "GOT MSG ", msg
        if msg[1]:
            self.state = 0
        else:
            self.state = 1

        for output in self.outputs:
            print "SENDING TO OUTPUT"
            output((self,self.state))

    def __call__(self,val):
        self.channel.send(val)

class AndGate(Listener):
    def __init__(self,outputs=None):
        Listener.__init__(self)
        self.inputA = Input('inputA',self)
        self.inputB = Input('inputB',self)
        self.state = 0
        if outputs:
            self.outputs = outputs
        else:
            self.outputs = []
        

    def processMessage(self,msg):
        print "GOT MSG ", msg
        if msg[1]:
            self.state = 0
        else:
            self.state = 1

        for output in self.outputs:
            print "SENDING TO OUTPUT"
            output((self,self.state))

    def __call__(self,val):
        self.channel.send(val)

if __name__ == "__main__":
    inverterA = Inverter(outputs=[Inverter()])
    inverterA.inputA(1)
    print '----------'
    inverterA.inputA(0)

