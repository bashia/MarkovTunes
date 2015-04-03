from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.template import Template

def uploadpage(request):
    return render(request,'markovtunes/index.html')

def uploadhandler(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form})


def input(request):
    fp = open("/Users/darius/MarkovTunes/markovtunes/markovtunes/static/audioeditor/index.html")
    a = fp.read()
    fp.close()
    return HttpResponse(a)
