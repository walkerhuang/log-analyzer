from django.db import models
from django.db.models.fields.related import ForeignKey
from django.core.files import File
from datetime import *
import re
# Create your models here.

class Log(models.Model):
    name = models.CharField(max_length=50)
    logfile = models.FileField()
    version = models.CharField(max_length=10)
    padv = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
    
 
    def parse_log(self):
        f = File(self.logfile)
        line = f.readline().decode('GBK')
        output_flag = 0
        cmd = Cmd()
        while('' != line):
            if(output_flag):
                if(cmd.is_exit(line)):
                    output_flag = 0
                    cmd.exit = cmd.get_exitcode(line)
                    cmd.duration = cmd.get_duration(line)
                    cmd.log = self
                    cmd.save()
                else:
                    cmd.output += line
                    
            if(cmd.is_cmd(line)):
                cmd = Cmd()
                cmd.name = cmd.get_cmd(line)
                cmd.time = cmd.get_time(line)
                
            if(cmd.is_output(line)):
                output_flag = 1
            line = f.readline().decode('GBK')
        
        return


class Cmd(models.Model):
    log = models.ForeignKey(Log)
    name = models.CharField(max_length=100)
    time = models.TimeField()
    output = models.CharField(max_length=200)
    duration = models.CharField(max_length=10)
    exit = models.CharField(max_length=5)
    
    def __str__(self):
        return self.name
    
    def is_cmd(self, line):
        pattern = re.compile(r'.* cmd')
        if(self.is_exit(line) or self.is_output(line)):
            return 0
        return pattern.match(line)
    
    def is_exit(self, line):
        pattern = re.compile(r'.* cmd exit=')
        
        return pattern.match(line)
    
    def is_output(self, line):
        pattern = re.compile(r'.* cmd stdout=')
        return pattern.match(line)
    
    def get_duration(self, line):
        m = re.match(r'.*duration: (.*) seconds', line)
        return m.groups()[0]
    
    def get_cmd(self, line):
        m = re.match(r'.* cmd (.*)', line)
        return m.groups()[0]
    
    def get_exitcode(self, line):
        m = re.match(r'.*cmd exit=(\d)', line)
        return m.groups()[0]
    
    def get_time(self, line):
        m = re.match(r'.* (\d\d:\d\d:\d\d) .*', line)
        str_times = m.groups()[0].split(':')
        tm = time(int(str_times[0]), int(str_times[1]), int(str_times[2]))
        
        return tm
    
