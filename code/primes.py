from time import time
import sys

def isPrime(number):
    for i in range(2,number//2):
        if number % i == 0:
            return False
    return True

def calcPrimes(start,end):
    totalPrimes = 0.0
    startTime = time()
    for i in range(start,end):
        if isPrime(i):
            totalPrimes += 1
            print "%i (%0.2f per second)" % (i,totalPrimes/(time()-startTime))

start,end=int(sys.argv[1]),int(sys.argv[2])
print start,end
calcPrimes(start,end)
