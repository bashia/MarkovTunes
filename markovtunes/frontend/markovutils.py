from django import forms
import os
import sys
import markov

def generateWavandKey(): 
    content = markov.main()
    contentsize = sys.getsizeof(content)
    key = ""


    return [content,contentsize,key]
