#
# pingpong_stackless.py
#

import stackless

ping_channel = stackless.channel()
pong_channel = stackless.channel()

def ping():
    while ping_channel.receive(): #blocks here
        print "PING"
        pong_channel.send("from ping")

def pong():
    while pong_channel.receive():
        print "PONG"
        ping_channel.send("from pong")



stackless.tasklet(ping)()
stackless.tasklet(pong)()

# we need to 'prime' the game by sending a start message
# if not, both tasklets will block
stackless.tasklet(ping_channel.send)('startup')

stackless.run()




