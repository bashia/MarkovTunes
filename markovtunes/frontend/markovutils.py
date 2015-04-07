from django import forms
import os

def generateWav(): #Placeholder for now, return wav file-formatted sound array for production
    content = []
    contentsize = 0
    contentpath = 'blarg.wav'
    with open(contentpath, 'rb') as file:
        content = file.read()
        contentsize = os.stat(contentpath).st_size
    return [content,contentsize]
