from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.template import Template
from uploadutils import UploadFileForm, handlefile

from django.views.decorators.csrf import csrf_exempt #DO NOT PUT THIS INTO PRODUCTION!!!

@csrf_exempt
def uploadpage(request):
    return render(request,'markovtunes/index.html')

@csrf_exempt
def uploadhandler(request):

    return HttpResponseRedirect('/')

@csrf_exempt
def iterate(request):
    return render(request,'markovtunes/iterate.html')

# if request.method == 'POST':
#     print("Posting"+ request)
#     form = UploadFileForm(request.POST, request.FILES)
#     if form.is_valid():
#         print ("valid form")
#         handlefile(request.FILES['wavfile'])
#         return HttpResponseRedirect('/iterate')
#     else:
#         print("invalid form")
# else:
#     form = UploadFileForm()
