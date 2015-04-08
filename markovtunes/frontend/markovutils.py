from django import forms
import os
import sys
import markov

def generateWavandKey(): #Placeholder for now, return wav file-formatted sound array for production
    content = markov.main()
    contentsize = sys.getsizeof(content)
    key = ""


    return [content,contentsize,key]
