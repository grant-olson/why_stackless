import stackless
from simpleMessageSocket import *

def ATM():
    while 1:
        print "Welcome to the Stackless Banking ATM Network!"
        print
        name = raw_input("Please enter your name or account number: ")
        
        action = raw_input("(D)eposit or (W)ithdrawal? ")
        if not action.startswith("D") and not action.startswith("W"):
            print "Invalid selection\n"
            continue
        elif action.startswith("D"):
            action = "CREDIT"
        else:
            action = "DEBIT"
            
        amount = raw_input("Amount: ")
        if not int(amount):
            print "Invalid amount\n"
            continue

        message = "%s|%s|%s" % (name,action,amount)
        sendMessage("127.0.0.1",3000,message)
        print
        print "Thank you for banking with Stackless Bank"
        print

if __name__ == "__main__":
    ATM()