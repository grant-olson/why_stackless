import pygame
import pygame.locals
import os, sys
import stackless
import math
import time

class actor:
    def __init__(self):
        self.channel = stackless.channel()
        self.processMessageMethod = self.defaultMessageAction
        stackless.tasklet(self.processMessage)()

    def processMessage(self):
        while 1:
            self.processMessageMethod(self.channel.receive())
        
    def defaultMessageAction(self,args):
        print args

class properties:
    def __init__(self,name,location=(-1,-1),angle=0,
                 velocity=0,height=-1,width=-1,hitpoints=1,public=True):
        self.name = name
        self.location = location
        self.angle = angle
        self.velocity = velocity
        self.height = height
        self.width = width
        self.public = public
        self.hitpoints = hitpoints

class worldState:
    def __init__(self,framerate,time):
        self.framerate = framerate
        self.time = time
        self.actors = []

class world(actor):
    def __init__(self):
        actor.__init__(self)
        self.registeredActors = {}
        self.framerate = 30
        self.maxframerate = 30
        stackless.tasklet(self.runFrame)()

    def testForCollision(self,x,y,item,otherItems=[]):
        if x < 0 or x + item.width > 496:
            return self.channel
        elif y < 0 or y+ item.height > 496:
            return self.channel
        else:
            ax1,ax2,ay1,ay2 = x, x+item.width, y,y+item.height
            for item,bx1,bx2,by1,by2 in otherItems:
                for x,y in [(ax1,ay1),(ax1,ay2),(ax2,ay1),(ax2,ay2)]:
                    if x >= bx1 and x <= bx2 and y >= by1 and y <= by2:
                        return item
            return None

    def killDeadActors(self):
        for actor in self.registeredActors.keys():
            if self.registeredActors[actor].hitpoints <= 0:
                print "ACTOR DIED", self.registeredActors[actor].hitpoints
                actor.send_exception(TaskletExit)
                del self.registeredActors[actor]

    def updateActorPositions(self):
        actorPositions = []
        for actor in self.registeredActors.keys():
            actorInfo = self.registeredActors[actor]
            if actorInfo.public:
                x,y = actorInfo.location
                angle = actorInfo.angle
                velocity = actorInfo.velocity
                VectorX,VectorY = (math.sin(math.radians(angle)) * velocity,
                                   math.cos(math.radians(angle)) * velocity)
                x += VectorX/self.framerate
                y -= VectorY/self.framerate
                collision = self.testForCollision(x,y,actorInfo,actorPositions)
                if collision:
                    #don't move
                    self.registeredActors[actor].hitpoints -= 1
                    actor.send((self.channel,"COLLISION",actor,collision))
                    if collision and collision is not self.channel:
                        self.registeredActors[collision].hitpoints -= 1
                        collision.send((self.channel,"COLLISION",actor,collision))
                else:                        
                    actorInfo.location = (x,y)
                actorPositions.append( (actor,
                                        actorInfo.location[0],
                                        actorInfo.location[0] + actorInfo.height,
                                        actorInfo.location[1],
                                        actorInfo.location[1] + actorInfo.width))

    def sendStateToActors(self,starttime):
        WorldState = worldState(self.framerate,starttime)
        for actor in self.registeredActors.keys():
            if self.registeredActors[actor].public:
                WorldState.actors.append( (actor, self.registeredActors[actor]) )
        for actor in self.registeredActors.keys():
            actor.send( (self.channel,"WORLD_STATE",WorldState) )

    def runFrame(self):
        initialStartTime = time.clock()
        startTime = time.clock()
        while 1:
            self.killDeadActors()
            self.updateActorPositions()
            self.sendStateToActors(startTime)
            #wait
            calculatedEndTime = startTime + 1.0/self.framerate

            doneProcessingTime = time.clock()
            percentUtilized =  (doneProcessingTime - startTime) / (1.0/self.framerate)
            if percentUtilized >= 1:
                self.framerate -= 1
                print "TOO MUCH LOWERING FRAME RATE: " , self.framerate
            elif percentUtilized <= 0.6 and self.framerate < self.maxframerate:
                self.framerate += 1
                print "TOO MUCH FREETIME, RAISING FRAME RATE: " , self.framerate

            while time.clock() < calculatedEndTime:
                pass
            startTime = calculatedEndTime
            
            stackless.schedule()

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "JOIN":
            print 'ADDING ' , msgArgs
            self.registeredActors[sentFrom] = msgArgs[0]
        elif msg == "UPDATE_VECTOR":
            self.registeredActors[sentFrom].angle = msgArgs[0]
            self.registeredActors[sentFrom].velocity = msgArgs[1]
        elif msg == "COLLISION":
            pass # known, but we don't do anything
        else:
            print '!!!! WORLD GOT UNKNOWN MESSAGE ' , args
            
World = world()

class display(actor):
    def __init__(self):
        actor.__init__(self)

        self.icons = {}
        pygame.init()

        window = pygame.display.set_mode((496,496))
        pygame.display.set_caption("Actor Demo")
        
        World.channel.send((self.channel,"JOIN",
                            properties(self.__class__.__name__,
                                       public=False)))

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            self.updateDisplay(msgArgs)
        else:
            print "UNKNOWN MESSAGE", args

    def getIcon(self, iconName):
        if self.icons.has_key(iconName):
            return self.icons[iconName]
        else:
            iconFile = os.path.join("data","%s.bmp" % iconName)
            surface = pygame.image.load(iconFile)
            surface.set_colorkey((0xf3,0x0a,0x0a))
            self.icons[iconName] = surface
            return surface

    def updateDisplay(self,msgArgs):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            
        screen = pygame.display.get_surface()

        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((200, 200, 200))

        screen.blit(background, (0,0))

        WorldState = msgArgs[0]

        for channel,item in WorldState.actors:
            screen.blit(pygame.transform.rotate(self.getIcon(item.name),-item.angle), item.location)
        pygame.display.flip()

Display = display()

class basicRobot(actor):
    def __init__(self,location=(0,0),angle=135,velocity=1,hitpoints=20):
        actor.__init__(self)
        self.location = location
        self.angle = angle
        self.velocity = velocity
        self.hitpoints = hitpoints
        World.channel.send((self.channel,"JOIN",
                            properties(self.__class__.__name__,
                                       location=self.location,
                                       angle=self.angle,
                                       velocity=self.velocity,
                                       height=32,width=32,hitpoints=self.hitpoints)))

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            for actor in msgArgs[0].actors:
                if actor[0] is self: break
            self.location = actor[1].location
            self.angle += 30.0 * (1.0 / msgArgs[0].framerate)
            if self.angle >= 360:
                self.angle -= 360
            World.channel.send((self.channel, "UPDATE_VECTOR", self.angle,self.velocity))
        elif msg == "COLLISION":
            self.angle += 73.0
            if self.angle >= 360:
                self.angle -= 360
            self.hitpoints -= 1
        else:
            print "UNKNOWN MESSAGE", args

basicRobot(angle=135,velocity=150)
basicRobot((464,0),angle=225,velocity=300)
basicRobot((100,200),angle=78,velocity=500)
basicRobot((400,300),angle=298,velocity=5)
basicRobot((55,55),angle=135,velocity=150)
basicRobot((464,123),angle=225,velocity=300)
basicRobot((180,200),angle=78,velocity=500)
basicRobot((400,380),angle=298,velocity=5)
    
stackless.run()

