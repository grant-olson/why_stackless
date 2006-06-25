import pygame
import pygame.locals
import os, sys
import stackless
import math
import time
import random

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
                 velocity=0,height=-1,width=-1,hitpoints=1,physical=True,
                 public=True):
        self.name = name
        self.location = location
        self.angle = angle
        self.velocity = velocity
        self.height = height
        self.width = width
        self.public = public
        self.hitpoints = hitpoints
        self.physical = physical

class worldState:
    def __init__(self,updateRate,time):
        self.updateRate = updateRate
        self.time = time
        self.actors = []

class world(actor):
    def __init__(self):
        actor.__init__(self)
        self.registeredActors = {}
        self.updateRate = 30
        self.maxupdateRate = 30
        stackless.tasklet(self.runFrame)()

    def testForCollision(self,x,y,item,otherItems=[]):
        if x < 0 or x + item.width > 496:
            return self.channel
        elif y < 0 or y+ item.height > 496:
            return self.channel
        else:
            ax1,ax2,ay1,ay2 = x, x+item.width, y,y+item.height
            for item,bx1,bx2,by1,by2 in otherItems:
                if self.registeredActors[item].physical == False: continue
                for x,y in [(ax1,ay1),(ax1,ay2),(ax2,ay1),(ax2,ay2)]:
                    if x >= bx1 and x <= bx2 and y >= by1 and y <= by2:
                        return item
                for x,y in [(bx1,by1),(bx1,by2),(bx2,by1),(bx2,by2)]:
                    if x >= ax1 and x <= ax2 and y >= ay1 and y <= ay2:
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
            if actorInfo.public and actorInfo.physical:
                x,y = actorInfo.location
                angle = actorInfo.angle
                velocity = actorInfo.velocity
                VectorX,VectorY = (math.sin(math.radians(angle)) * velocity,
                                   math.cos(math.radians(angle)) * velocity)
                x += VectorX/self.updateRate
                y -= VectorY/self.updateRate
                collision = self.testForCollision(x,y,actorInfo,actorPositions)
                if collision:
                    #don't move
                    actor.send((self.channel,"COLLISION",actor,collision))
                    if collision and collision is not self.channel:
                        collision.send((self.channel,"COLLISION",actor,collision))
                else:                        
                    actorInfo.location = (x,y)
                actorPositions.append( (actor,
                                        actorInfo.location[0],
                                        actorInfo.location[0] + actorInfo.height,
                                        actorInfo.location[1],
                                        actorInfo.location[1] + actorInfo.width))

    def sendStateToActors(self,starttime):
        WorldState = worldState(self.updateRate,starttime)
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
            calculatedEndTime = startTime + 1.0/self.updateRate

            doneProcessingTime = time.clock()
            percentUtilized =  (doneProcessingTime - startTime) / (1.0/self.updateRate)
            if percentUtilized >= 1:
                self.updateRate -= 1
                print "TOO MUCH LOWERING FRAME RATE: " , self.updateRate
            elif percentUtilized <= 0.6 and self.updateRate < self.maxupdateRate:
                self.updateRate += 1
                print "TOO MUCH FREETIME, RAISING FRAME RATE: " , self.updateRate

            while time.clock() < calculatedEndTime:
                stackless.schedule()
            startTime = calculatedEndTime
            
            stackless.schedule()

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "JOIN":
            self.registeredActors[sentFrom] = msgArgs[0]
        elif msg == "UPDATE_VECTOR":
            self.registeredActors[sentFrom].angle = msgArgs[0]
            self.registeredActors[sentFrom].velocity = msgArgs[1]
        elif msg == "COLLISION":
            pass # known, but we don't do anything
        elif msg == "KILLME":
            self.registeredActors[sentFrom].hitpoints = 0
        else:
            print '!!!! WORLD GOT UNKNOWN MESSAGE ' , msg, msgArgs
            
World = world().channel

class display(actor):
    def __init__(self,world=World):
        actor.__init__(self)

        self.world = World
        self.icons = {}
        pygame.init()

        window = pygame.display.set_mode((496,496))
        pygame.display.set_caption("Actor Demo")
        
        self.world.send((self.channel,"JOIN",
                            properties(self.__class__.__name__,
                                       public=False)))

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            self.updateDisplay(msgArgs)
        else:
            print "DISPLAY UNKNOWN MESSAGE", args

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
            itemImage = self.getIcon(item.name)
            itemImage = pygame.transform.rotate(itemImage,-item.angle)
            screen.blit(itemImage, item.location)
        pygame.display.flip()

display()

class basicRobot(actor):
    def __init__(self,location=(0,0),angle=135,velocity=1,
                 hitpoints=20,world=World):
        actor.__init__(self)
        self.location = location
        self.angle = angle
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.world = world
        self.world.send((self.channel,"JOIN",
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
            self.angle += 30.0 * (1.0 / msgArgs[0].updateRate)
            if self.angle >= 360:
                self.angle -= 360
                
            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle,self.velocity)
            self.world.send(updateMsg)
        elif msg == "COLLISION":
            self.angle += 73.0
            if self.angle >= 360:
                self.angle -= 360
            self.hitpoints -= 1
            if self.hitpoints <= 0:
                explosion(self.location,self.angle)
                self.world.send((self.channel, "KILLME"))
        elif msg == "DAMAGE":
            self.hitpoints -= msgArgs[0]
            if self.hitpoints <= 0:
                explosion(self.location,self.angle)
                self.world.send( (self.channel,"KILLME") )
                
        else:
            print "BASIC ROBOT UNKNOWN MESSAGE", args

class explosion(actor):
    def __init__(self,location=(0,0),angle=0,world=World):
        actor.__init__(self)
        self.time = 0.0
        self.world = world
        self.world.send((self.channel,"JOIN",
                            properties(self.__class__.__name__,
                                       location = location,
                                       angle = angle,
                                       velocity=0,
                                       height=32.0,width=32.0,hitpoints=1,
                                       physical=False)))
                           
    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            WorldState = msgArgs[0]
            if self.time == 0.0:
                self.time = WorldState.time
            elif WorldState.time >= self.time + 3.0:
                self.world.send( (self.channel, "KILLME") )

class mine(actor):
    def __init__(self,location=(0,0),world=World):
        actor.__init__(self)
        self.world = world
        self.world.send((self.channel,"JOIN",
                            properties(self.__class__.__name__,
                                       location=location,
                                       angle=0,
                                       velocity=0,
                                       height=2.0,width=2.0,hitpoints=1)))

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            pass                
        elif msg == "COLLISION":
            if msgArgs[0] is self.channel:
                other = msgArgs[1]
            else:
                other = msgArgs[0]
            other.send( (self.channel,"DAMAGE",25) )
            self.world.send( (self.channel,"KILLME"))
            print "MINE COLLISION"
        else:
            print "UNKNOWN MESSAGE", args

class minedropperRobot(actor):
    def __init__(self,location=(0,0),angle=135,velocity=1,
                 hitpoints=20,world=World):
        actor.__init__(self)
        self.location = location
        self.angle = angle
        self.delta = 0.0
        self.height=32.0
        self.width=32.0
        self.deltaDirection = "up"
        self.nextMine = 0.0
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.world = world
        self.world.send((self.channel,"JOIN",
                            properties(self.__class__.__name__,
                                       location=self.location,
                                       angle=self.angle,
                                       velocity=self.velocity,
                                       height=self.height,width=self.width,
                                       hitpoints=self.hitpoints)))

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            for actor in msgArgs[0].actors:
                if actor[0] is self.channel:
                    break
            self.location = actor[1].location
            if self.deltaDirection == "up":
                self.delta += 60.0 * (1.0 / msgArgs[0].updateRate)
                if self.delta > 15.0:
                    self.delta = 15.0
                    self.deltaDirection = "down"
            else:
                self.delta -= 60.0 * (1.0 / msgArgs[0].updateRate)
                if self.delta < -15.0:
                    self.delta = -15.0
                    self.deltaDirection = "up"
            if self.nextMine <= msgArgs[0].time:
                self.nextMine = msgArgs[0].time + 1.0
                mineX,mineY = (self.location[0] + (self.width / 2.0) ,
                               self.location[1] + (self.width / 2.0))

                mineDistance = (self.width / 2.0 ) ** 2
                mineDistance += (self.height / 2.0) ** 2
                mineDistance = math.sqrt(mineDistance)

                VectorX,VectorY = (math.sin(math.radians(self.angle + self.delta)),
                                   math.cos(math.radians(self.angle + self.delta)))
                VectorX,VectorY = VectorX * mineDistance,VectorY * mineDistance
                x,y = self.location
                x += self.width / 2.0
                y += self.height / 2.0
                x -= VectorX
                y += VectorY
                mine( (x,y))
                
            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle + self.delta ,self.velocity)
            self.world.send(updateMsg)
        elif msg == "COLLISION":
            self.angle += 73.0
            if self.angle >= 360:
                self.angle -= 360
            self.hitpoints -= 1
            if self.hitpoints <= 0:
                explosion(self.location,self.angle)
                self.world.send((self.channel,"KILLME"))
        elif msg == "DAMAGE":
            self.hitpoints -= msgArgs[0]
            if self.hitpoints <= 0:
                explosion(self.location,self.angle)
                self.world.send((self.channel, "KILLME"))
        else:
            print "UNKNOWN MESSAGE", args

class spawner(actor):
    def __init__(self,location=(0,0),world=World):
        actor.__init__(self)
        self.location = location
        self.time = 0.0
        self.world = world
        
        self.robots = []
        for name,klass in globals().iteritems():
            if name.endswith("Robot"):
                self.robots.append(klass)

        self.world.send((self.channel,"JOIN",
                            properties(self.__class__.__name__,
                                       location = location,
                                       angle=0,
                                       velocity=0,
                                       height=32.0,width=32.0,hitpoints=1,
                                       physical=False)))

    def defaultMessageAction(self,args):    
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            WorldState = msgArgs[0]
            if self.time == 0.0:
                self.time = WorldState.time + 0.5 # wait 1/2 second on start
            elif WorldState.time >= self.time: # every five seconds
                self.time = WorldState.time + 5.0
                angle = random.random() * 360.0
                velocity = random.random() * 1000.0
                newRobot = random.choice(self.robots)
                newRobot(self.location,angle,velocity)

spawner( (32,32) )
spawner( (432,32) )
spawner( (32,432) )
spawner( (432,432) )
spawner( (232,232) )
    
stackless.run()

