import pygame
import pygame.locals
import os, sys
import stackless
import math

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

class world(actor):
    def __init__(self):
        actor.__init__(self)
        self.registeredActors = {}
        stackless.tasklet(self.sendStateToActors)()

    def testForCollision(self,x,y):
        if x < 0 or x > 496:
            return 1
        elif y < 0 or y > 496:
            return 1
        else:
            return 0
    
    def sendStateToActors(self):
        while 1:
            for actor in self.registeredActors.keys():
                actorInfo = self.registeredActors[actor]
                if self.registeredActors[actor][1] != (-1,-1):
                    VectorX,VectorY = (math.sin(math.radians(actorInfo[2])) * actorInfo[3],
                                       math.cos(math.radians(actorInfo[2])) * actorInfo[3])
                    x,y = actorInfo[1]
                    x += VectorX
                    y -= VectorY
                    if self.testForCollision(x,y):
                        actor.send((self.channel,"COLLISION"))
                    else:                        
                        self.registeredActors[actor] = tuple([actorInfo[0],
                                                          (x,y),
                                                              actorInfo[2],
                                                              actorInfo[3]])
            worldState = [self.channel, "WORLD_STATE"]
            for actor in self.registeredActors.keys():
                if self.registeredActors[actor][1] != (-1,-1):
                    worldState.append( (actor, self.registeredActors[actor]))
            message = tuple(worldState)
            for actor in self.registeredActors.keys():
                actor.send(message)
            stackless.schedule()

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "JOIN":
            print 'ADDING ' , msgArgs
            self.registeredActors[sentFrom] = msgArgs
        elif msg == "UPDATE_VECTOR":
            self.registeredActors[sentFrom] = tuple([self.registeredActors[sentFrom][0],
                                                     self.registeredActors[sentFrom][1],
                                                     msgArgs[0],msgArgs[1]])
        else:
            print '!!!! WORLD GOT UNKNOWN MESSAGE ' , args
            
World = world().channel

class display(actor):
    def __init__(self,world=World):
        actor.__init__(self)

        self.world = World

        self.icons = {}
        pygame.init()

        window = pygame.display.set_mode((496,496))
        pygame.display.set_caption("Actor Demo")

        joinMsg = (self.channel,"JOIN",self.__class__.__name__, (-1,-1))
        self.world.send(joinMsg)

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

    def updateDisplay(self,actors):

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            
        screen = pygame.display.get_surface()

        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((200, 200, 200))

        screen.blit(background, (0,0))
        for item in actors:
            screen.blit(pygame.transform.rotate(self.getIcon(item[1][0]),-item[1][2]), item[1][1])
        pygame.display.flip()

display()

class basicRobot(actor):
    def __init__(self,location=(0,0),angle=135,velocity=1,world=World):
        actor.__init__(self)
        self.location = location
        self.angle = angle
        self.velocity = velocity
        self.world = world
        self.vector = self.vectorFromAngleAndVelocity()

        joinMsg =(self.channel,"JOIN",self.__class__.__name__,
                  self.location,self.angle,self.velocity)
        self.world.send(joinMsg)

    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            self.location = (self.location[0] + 1, self.location[1] + 1)
            self.angle += 1
            if self.angle >= 360:
                self.angle -= 360
            self.vector = self.vectorFromAngleAndVelocity()

            updateMsg = (self.channel, "UPDATE_VECTOR",
                         self.angle,self.velocity)
            self.world.send(updateMsg)
        elif msg == "COLLISION":
            self.angle += 73
            if self.angle >= 360:
                self.angle -= 360
            self.vector = self.vectorFromAngleAndVelocity()
        else:
            print "UNKNOWN MESSAGE", args

basicRobot(angle=135,velocity=5)
basicRobot((464,0),angle=225,velocity=10)

    
stackless.run()

