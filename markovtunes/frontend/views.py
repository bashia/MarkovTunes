from django.shortcuts import render,render_to_response,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template
from uploadutils import UploadFileForm, handlefile
import markovutils
import json
import os
import picklejar
from django.views.decorators.csrf import csrf_exempt #DO NOT PUT THIS INTO PRODUCTION!!!

@csrf_exempt
def uploadpage(request):
    return render(request,'markovtunes/index.html')

@csrf_exempt
def uploadhandler(request): # Assuming best intentions (use AWS' IP host restriction feature for demo,live testing)


    form = UploadFileForm(request.POST, request.FILES)
    handlefile(request.FILES['wavfile'])

    markovutils.generateMarkovModel()

    response = HttpResponse('iterate')
    response['redirect'] = 'iterate'

    return response

@csrf_exempt
def iterate(request):
    return render(request,'markovtunes/iterate.html')

@csrf_exempt
def sendnewtrack(request):

    response = HttpResponse()
    wavbytes = markovutils.generateWav()
    response.write(wavbytes.read())
    response['Content-Type'] ='audio/wav'
    return response

@csrf_exempt
def integratefeedback(request):

    #Access global Markov Model somehow, call its methods with request data as parameters

    feedback = json.loads(request.body)

    liked = [ [elem['start'], elem['end']] for elem in feedback['liked']]
    #disliked =  [ [elem['start'], elem['end']] for elem in feedback['disliked']]

    markovutils.updateModel(liked)

    response = HttpResponse('iterate')
    response['redirect'] = 'iterate'
    return response
