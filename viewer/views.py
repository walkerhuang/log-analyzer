from django.shortcuts import render
from django import forms
from .models import Record
from django.http import HttpResponse, HttpResponseRedirect
import os
# Create your views here.

class RecordForm(forms.Form):
    name = forms.CharField(max_length=20)
    recordfile = forms.FileField()
    
def detail(req, pk):
    record = Record.objects.get(pk=pk)
    return render(req, 'detail.html', {'record':record})

def index(req):
    records = Record.objects.all()
    return render(req, 'index.html', {'records':records})

def delete(req, pk):
    record = Record.objects.get(pk=pk)
    record.delete()
    return HttpResponseRedirect('/viewer/')

def add(req):
    if(req.method=='POST'):
        rf = RecordForm(req.POST, req.FILES)
        if (rf.is_valid()):
            record = Record()
            record.file = rf.cleaned_data["recordfile"]
            (filepath, filename) = os.path.split(record.file.name)
            record.name = filename.split('.')[0]
            record.save()
            record.extract(record.file.path)
            record.parse_record()
            #log.parse_log()
            return HttpResponseRedirect('/viewer/')
        else:
            return HttpResponse('failed')
    else:
        rf = RecordForm();
        return render(req, 'add.html', {'rf': rf})