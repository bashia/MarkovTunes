from django.shortcuts import render,render_to_response,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template
from uploadutils import UploadFileForm, handlefile
from markovutils import generateWav

from django.views.decorators.csrf import csrf_exempt #DO NOT PUT THIS INTO PRODUCTION!!!

@csrf_exempt
def uploadpage(request):
    return render(request,'markovtunes/index.html')

@csrf_exempt
def uploadhandler(request): # Assuming best intentions (use AWS' IP host restriction feature for demo,live testing)


    form = UploadFileForm(request.POST, request.FILES)
    handlefile(request.FILES['wavfile'])

    #return HttpResponseRedirect('/iterate')
    response = HttpResponse('iterate')
    response['redirect'] = 'iterate'

    return response

    # if request.method == 'POST': # Some more secure code
    #     print("Posting"+ request)
    #     # form = UploadFileForm(request.POST, request.FILES)
    #     # if form.is_valid():
    #     #     print ("valid form")
    #     #     handlefile(request.FILES['wavfile'])
    #     #     return HttpResponseRedirect('/iterate')
    #     # else:
    #     #     print("invalid form")
    # else:
    #     form = UploadFileForm()

@csrf_exempt
def iterate(request):
    return render(request,'markovtunes/iterate.html')

@csrf_exempt
def sendnewtrack(request):
    response = HttpResponse()
    responseData = generateWav()
    response.write(responseData[0])
    response['Content-Type'] ='audio/wav'
    response['Content-Length'] = responseData[1]
    #import pdb; pdb.set_trace()
    return response
