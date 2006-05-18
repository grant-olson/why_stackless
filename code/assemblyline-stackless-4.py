import stackless
##########

sleepingTasklets = []
sleepingTicks = 0

def Sleep(secondsToWait):
    channel = stackless.channel()
    endTime = sleepingTicks + secondsToWait
    sleepingTasklets.append((endTime, channel))
    sleepingTasklets.sort()
    # Block until we get sent an awakening notification.
    channel.receive()

def ManageSleepingTasklets():
    global sleepingTicks
    while 1:
        if len(sleepingTasklets):
            endTime = sleepingTasklets[0][0]
            while endTime <= sleepingTicks:
                channel = sleepingTasklets[0][1]
                del sleepingTasklets[0]
                # We have to send something, but it doesn't matter what as it is not used.
                channel.send(None)
                endTime = sleepingTasklets[0][0] # check next
        sleepingTicks += 1
        print "1 second passed"
        stackless.schedule()

stackless.tasklet(ManageSleepingTasklets)()

##########

class storeroom:
    def __init__(self,name,product,unit,count):
        self.product = product
        self.unit = unit
        self.count = count
        self.name = name

    def get(self,count):
        while count > self.count: #reschedule until we have enough
            print "%s doesn't have enough %s to deliver yet" % (self.name, self.product)
            stackless.schedule()
        self.count -= count
        return count

        return count            

    def put(self,count):
        self.count += count

    def run(self):
        pass

rivetStoreroom = storeroom("rivetStoreroom","rivets","#",1000)
plasticStoreroom = storeroom("plastic Storeroom","plastic pellets","lb",100)

class injectionMolder:
    def __init__(self,name,partName,plasticSource,plasticPerPart,timeToMold):
        self.partName = partName
        self.plasticSource = plasticSource
        self.plasticPerPart = plasticPerPart
        self.timeToMold = timeToMold
        self.plastic = 0
        self.items = 0
        self.name = name
        stackless.tasklet(self.run)()

    def get(self,items):
        while items > self.items: #reschedule until we have enough
            print "%s doesn't have enough %s to deliver yet" % (self.name, self.partName)
            stackless.schedule()
        self.items -= items
        return items

    def run(self):
        while 1:
            print "%s starts making new part %s" % (self.name,self.partName)
            if self.plastic < self.plasticPerPart:
                print "%s getting more plastic"
                self.plastic += self.plasticSource.get(self.plasticPerPart * 10)
            self.plastic -= self.plasticPerPart
            Sleep(self.timeToMold)
            print "%s done molding after %s seconds" % (self.partName, self.timeToMold)
            self.items += 1
            print "%s finished making part" % self.name
            stackless.schedule()
                

armMolder = injectionMolder("arm Molder", "arms",plasticStoreroom,0.2,5)
legMolder = injectionMolder("leg Molder", "leg",plasticStoreroom,0.2,5)
headMolder = injectionMolder("head Molder","head",plasticStoreroom,0.1,5)
torsoMolder = injectionMolder("torso Molder","torso",plasticStoreroom,0.5,10)


class assembler:
    def __init__(self,name,partAsource,partBsource,rivetSource,timeToAssemble):
        self.partAsource = partAsource
        self.partBsource = partBsource
        self.rivetSource = rivetSource
        self.timeToAssemble = timeToAssemble
        self.itemA = 0
        self.itemB = 0
        self.items = 0
        self.rivets = 0
        self.name = name
        stackless.tasklet(self.run)()

    def get(self,items):
        while items > self.items: #reschedule until we have enough
            print "Don't have a %s to deliver yet" % (self.name)
            stackless.schedule()
        self.items -= items
        return items
    
    def run(self):        
        while 1:
            print "%s starts assembling new part" % self.name
            self.itemA += self.partAsource.get(1)
            self.itemB += self.partBsource.get(1)
            print "%s starting to assemble" % self.name
            Sleep(self.timeToAssemble)
            print "%s done assembling after %s" % (self.name, self.timeToAssemble)
            self.items += 1
            print "%s finished assembling part" % self.name
            stackless.schedule()
            
legAssembler = assembler("leg Assembler",torsoMolder,legMolder,rivetStoreroom,2)
armAssembler = assembler("arm Assembler", armMolder,legAssembler,rivetStoreroom,2)
torsoAssembler = assembler("torso Assembler", headMolder,armAssembler,rivetStoreroom,3)

components = [rivetStoreroom, plasticStoreroom, armMolder, legMolder, headMolder, torsoMolder,
              legAssembler, armAssembler, torsoAssembler]

def pause():
    while 1:
        raw_input("Press <ENTER> to continue...")
        print "\n\n\n"
        stackless.schedule()

stackless.tasklet(pause)()

def run():
    stackless.run()
    
