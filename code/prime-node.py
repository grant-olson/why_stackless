from simpleMessageSocket import *
import stackless
import sys

def isPrime(number):
    for i in range(2,number//2):
        if number % i == 0:
            return False
    return True

def checkPrime(number):
    if isPrime(number):
        result = "TRUE"
    else:
        result = "FALSE"
    answer = "ANSWER|%s|%s" % (number,result)
    sendMessage(serverIp,serverPort,answer)

def nodeProcessMessage(msg):
    msg = msg.split("|")
    cmd,args = msg[0],msg[1:]
    if cmd == "ASK":
        stackless.tasklet(checkPrime)(int(args[0]))
    else:
        print "UNKNOWN MESSAGE", msg
    
if __name__ == "__main__":
    nodeIp,nodePort,serverIp,serverPort = sys.argv[1:]
    nodePort,serverPort = int(nodePort),int(serverPort)

    stackless.tasklet(getMessages)(nodeIp,nodePort,nodeProcessMessage)
    sendMessage(serverIp,serverPort,"JOIN|%s|%s" % (nodeIp,nodePort))
    stackless.run()