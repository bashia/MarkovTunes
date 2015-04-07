from django import forms

basefilepath = "blarg.wav"

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

def handlefile(f):
    with open(basefilepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
