#!/usr/bin/python

import pickle
import sqlite3 as lite
import sys
import markov

class system:

    def __init__(self):
        return

    def write(self,id,object):
        filename = str(id) + ".p"
        pickle.dump(object,open(filename,"wb"))
        return filename

    def read(self,filename):
        object = pickle.load(open(filename,"rb"))
        return object

    def testRW(self):
        print "testRW()"
        list = [[1,2],[3,4]]
        file = self.write(1,list)
        list2 = self.read(file)
        print list2

def main():
    # print ("running picklejar")

    picklejar = system()
    #picklejar.testRW()

    # thing1 = markov.system([],[],[],[],[],[],[],[],[],0,[])
    # name = picklejar.write(12456,thing1)
    # print name
    # thing2 = picklejar.read(name)

    return

if __name__ == "__main__":
    main()
