from django.shortcuts import render
from django import forms
from .models import Log
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.

class LogForm(forms.Form):
    name = forms.CharField(max_length=20)
    logfile = forms.FileField()
    
def detail(req, pk):
    log = Log.objects.get(pk=pk)
    return render(req, 'detail.html', {'log':log})

def index(req):
    logs = Log.objects.all()
    return render(req, 'index.html', {'logs':logs})


def add(req):
    if(req.method=='POST'):
        lf = LogForm(req.POST, req.FILES)
        if (lf.is_valid()):
            log = Log()
            log.logfile = lf.cleaned_data["logfile"]
            log.name = log.logfile
            log.save()
            log.parse_log()
            return HttpResponse('success')
        else:
            return HttpResponse('failed')
    else:
        lf = LogForm();
        return render(req, 'add.html', {'lf': lf})