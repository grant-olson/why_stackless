import stackless
from simpleMessageSocket import *

accounts = {}

def processBankMessage(msg):
    print msg
    user,type,amount = msg.split("|")
    if not accounts.has_key(user):
        accounts[user] = 0
    if type == "DEBIT":
        accounts[user] -= int(amount)
    elif type == "CREDIT":
        accounts[user] += int(amount)
    elif type == "BALANCE":
        pass
    else:
        print "UNKNOWN MESSAGE" , msg

stackless.tasklet(getMessages)(processBankMessage)
stackless.run()


    