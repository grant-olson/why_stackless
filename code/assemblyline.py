"""

assembly line

Storerooms
    plastic pellets - per pound
    rivits - #

Injection molders:
    Torso
    Head
    Arms
    Legs
    
Assemblers:
    Add legs
    Add arms
    Add heads
"""

class storeroom:
    def __init__(self,name,product,unit,count):
        self.product = product
        self.unit = unit
        self.count = count
        self.name = name

    def get(self,count):
        if count > self.count:
            raise RuntimeError("Not enough %s" % self.product)
        else:
            self.count -= count

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
        self.items = 0
        self.plastic = 0
        self.time = -1
        self.name = name

    def get(self,items):
        if items > self.items:
            return 0
        else:
            self.items -= items
            return items

    def run(self):
        if self.time == 0:
            self.items += 1
            print "%s finished making part" % self.name
            self.time -= 1
        elif self.time < 0:
            print "%s starts making new part %s" % (self.name,self.partName)
            if self.plastic < self.plasticPerPart:
                print "%s getting more plastic"
                self.plastic += self.plasticSource.get(self.plasticPerPart * 10)
            self.time = self.timeToMold
        else:
            print "%s molding for %s more seconds" % (self.partName, self.time)
            self.time -= 1
                

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
        self.time = -1
        self.name = name

    def get(self,items):
        if items > self.items:
            return 0
        else:
            self.items -= items
            return items

    def run(self):
        if self.time == 0:
            self.items += 1
            print "%s finished assembling part" % self.name
            self.time -= 1
        elif self.time < 0:
            print "%s starts assembling new part" % self.name
            if self.itemA < 1:
                print "%s Getting item A" % self.name
                self.itemA += self.partAsource.get(1)
                if self.itemA < 1:
                    print "%s waiting for item A" % self.name
            elif self.itemB < 1:
                print "%s Getting item B" % self.name
                self.itemB += self.partBsource.get(1)
                if self.itemB < 1:
                    print "%s waiting for item B" % self.name
            print "%s starting to assemble" % self.name
            self.time = self.timeToAssemble
        else:
            print "%s assembling for %s more seconds" % (self.name, self.time)
            self.time -= 1
            
legAssembler = assembler("leg Assembler",torsoMolder,legMolder,rivetStoreroom,2)
armAssembler = assembler("arm Assembler", armMolder,legAssembler,rivetStoreroom,2)
torsoAssembler = assembler("torso Assembler", headMolder,armAssembler,rivetStoreroom,3)

components = [rivetStoreroom, plasticStoreroom, armMolder, legMolder, headMolder, torsoMolder,
              legAssembler, armAssembler, torsoAssembler]

def run():
    for component in components:
        component.run()

        

