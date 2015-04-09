from django import forms
import os
import sys
import markov
import picklejar

def generateWavandKey():
    content = markov.main().generatemelody()
    contentsize = sys.getsizeof(content)
    key = ""


    return [content,contentsize,key]


def generateMarkovModel():

    markovmodel = markov.main()

    markovmodel.generatemelody()
    pickler = picklejar.system()

    pickler.write("markovmodel",markovmodel)

def generateWav():

    unpickler = picklejar.system()

    markovmodel = unpickler.read("markovmodel.p")

    content = markovmodel.generatemelody()

    contentsize = sys.getsizeof(content)

    return [content,contentsize]

def updateModel(pairlist):

    pickler = picklejar.system()

    markovmodel = pickler.read("markovmodel.p")

    markovmodel.audio_update(pairlist)

    pickler.write('markovmodel',markovmodel)
