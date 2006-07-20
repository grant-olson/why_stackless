from simpleMessageSocket import *
import stackless
import sys, time

def isPrime(number):
    for i in range(2,number//2):
        if number % i == 0:
            return False
    return True

def checkPrime(number):
    if isPrime(number):
        answerChannel.send((number,"TRUE"))

nodes = ["server"]

def sendNodes(start,end):
    i = start
    while i <= end:
        if not nodes: # no available nodes, don't burn CPU
            print "sleeping"
            time.sleep(0.5)
        else:
            for node in nodes:
                if node == "server":
                    stackless.tasklet(checkPrime)(i)
                else:
                    try:
                        msg = "ASK|%s" % i
                        sendMessage(node[0],node[1],msg)
                    except:
                        print "COULDN'T SEND MESSAGE"
                        continue
                i += 1


        stackless.schedule()

answerChannel = stackless.channel()

def interpretAnswers():
    startTime = time.time()
    totalPrimes = 0
    while 1:
        answer = answerChannel.receive()
        if answer[1] == "TRUE":
            totalPrimes += 1
            print "%s (%0.2f per second)" % (answer[0],totalPrimes/(time.time()-startTime))

def serverMessageAction(msg):
    msg = msg.split("|")
    cmd,args = msg[0],msg[1:]
    if cmd == "JOIN":
        print "JOINING" , args
        node = (args[0],int(args[1]))
        nodes.append(node)
    elif cmd == "ANSWER":
        answerChannel.send(args)
    else:
        print "UNKNOWN MESSAGE" , msg

if __name__ == "__main__":
    start,end,server,port = sys.argv[1:]
    start,end,port = int(start),int(end),int(port)
    
    stackless.tasklet(sendNodes)(start,end)
    stackless.tasklet(getMessages)(server,port,serverMessageAction)
    stackless.tasklet(interpretAnswers)()
    stackless.run()
