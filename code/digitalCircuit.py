import stackless

debug=0
def debugPrint(x):
    if debug:print x

class EventHandler:
    def __init__(self,*outputs):
        if outputs==None:
            self.outputs=[]
        else:
            self.outputs=list(outputs)

        self.channel = stackless.channel()
        stackless.tasklet(self.listen)()

    def listen(self):
        while 1:
            val = self.channel.receive()
            self.processMessage(val)
            for output in self.outputs:
                self.notify(output)
                
    def processMessage(self,val):
        pass

    def notify(self,output):
        pass

    def registerOutput(self,output):
        self.outputs.append(output)
    
    def __call__(self,val):
        self.channel.send(val)

class Switch(EventHandler):
    def __init__(self,initialState=0,*outputs):
        EventHandler.__init__(self,*outputs)
        self.state = initialState

    def processMessage(self,val):
        debugPrint("Setting input to %s" % val)
        self.state = val

    def notify(self,output):
        output((self,self.state))

class Reporter(EventHandler):
    def __init__(self,msg="%(sender)s send message %(value)s"):
        EventHandler.__init__(self)
        self.msg = msg
        
    def processMessage(self,msg):
        sender,value=msg
        print self.msg % {'sender':sender,'value':value}

class Inverter(EventHandler):
    def __init__(self,input,*outputs):
        EventHandler.__init__(self,*outputs)
        self.input = input
        input.registerOutput(self)
        self.state = 0

    def processMessage(self,msg):
        sender,value = msg
        debugPrint("Inverter received %s from %s" % (value,msg))
        if value:
            self.state = 0
        else:
            self.state = 1

    def notify(self,output):
        output((self,self.state))

class AndGate(EventHandler):
    def __init__(self,inputA,inputB,*outputs):
        EventHandler.__init__(self,*outputs)

        self.inputA = inputA
        self.inputAstate = inputA.state
        inputA.registerOutput(self)
        
        self.inputB = inputB
        self.inputBstate = inputB.state
        inputB.registerOutput(self)
        
        self.state = 0

    def processMessage(self,msg):
        sender, value = msg
        debugPrint("AndGate received %s from %s" % (value,sender))
        
        if sender is self.inputA:
            self.inputAstate = value
        elif sender is self.inputB:
            self.inputBstate = value
        else:
            raise RuntimeError("Didn't expect message from %s" % sender)

        if self.inputAstate and self.inputBstate:
            self.state = 1
        else:
            self.state = 0
        debugPrint("AndGate's new state => %s" % self.state)
        
    def notify(self,output):
        output((self,self.state))

class OrGate(EventHandler):
    def __init__(self,inputA,inputB,*outputs):
        EventHandler.__init__(self,*outputs)

        self.inputA = inputA
        self.inputAstate = inputA.state
        inputA.registerOutput(self)
        
        self.inputB = inputB
        self.inputBstate = inputB.state
        inputB.registerOutput(self)
        
        self.state = 0

    def processMessage(self,msg):
        sender, value = msg
        debugPrint("OrGate received %s from %s" % (value,sender))
        
        if sender is self.inputA:
            self.inputAstate = value
        elif sender is self.inputB:
            self.inputBstate = value
        else:
            raise RuntimeError("Didn't expect message from %s" % sender)

        if self.inputAstate or self.inputBstate:
            self.state = 1
        else:
            self.state = 0
        debugPrint("OrGate's new state => %s" % self.state)

    def notify(self,output):
        output((self,self.state))


if __name__ == "__main__":
    print "\n\n\n-----------"
    input = Switch()
    inverterA = Inverter(input)
    inverterB = Inverter(inverterA,Reporter("Result => %(value)s"))
    input(1)
    print '----------'
    input (0)
    print "\n\n!!!!!!!!!!!!"
    inputA = Switch()
    inputB = Switch()
    reporter=Reporter("AndGate Result => %(value)s")
    andGate=AndGate(inputA,inputB,reporter)
    inputA(1)
    inputB(1)

    # half adder
    inputA = Switch()
    inputB = Switch()
    result = Reporter("Result = %(value)s")
    carry = Reporter("Carry = %(value)s")
    andGateA = AndGate(inputA,inputB,carry)
    orGate = OrGate(inputA,inputB)
    inverter = Inverter(andGateA)
    andGateB = AndGate(orGate,inverter,result)
    inputA(1)
    inputB(1)
    inputB(0)
    inputA(0)
    