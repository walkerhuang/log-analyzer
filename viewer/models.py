from django.db import models
from django.db.models.fields.related import ForeignKey
from django.core.files import File
from datetime import *
import re,tarfile,os,json
# Create your models here.

class Record(models.Model):
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to = './logs')
    version = models.CharField(max_length=10)
    padv = models.CharField(max_length=10)
    upload_time = models.DateTimeField(auto_now=True)
    excute_time = models.CharField(max_length=20)
    operation_time = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    
    @staticmethod
    def extract(file_path):
        try:
            tar = tarfile.open(file_path, "r")
            file_names = tar.getnames()
            for file_name in file_names:
                tar.extract(file_name, os.path.dirname(file_path))
            tar.close()
        except Exception as err:
            raise err
        
    def parse_json(self, filename):
        fh = open(filename)
        dicts = json.load(fh)
        padv = dicts['EDR']['padv']
        version = dicts['CPIC']['rel'][padv]['vers']
        systems = dicts['Cfg']['systems']
        self.padv = padv
        self.version = version
        for index, lf in enumerate(self.logfile_set.all()):
            lf.host = systems[index]
            lf.save()
    
    def parse_metrics(self, filename):
        fh = open(filename)
        dicts = json.load(fh)
        self.excute_time = dicts['Summary']['Total']['Execute_Time']
        self.operation_time = dicts['Summary']['Total']['Operations_Time']
        
    
    def parse_record(self):
        uncompress_file = os.path.dirname(self.file.path)
        uncompress_file = os.path.join(uncompress_file, self.name)
        log_pattern = re.compile(r'log[1-9]')
        
        for parent,dirname,filenames in os.walk(uncompress_file):
            for filename in filenames:
                suffix = filename.split('.')[-1]
                if log_pattern.match(suffix):
                    lf = LogFile()
                    lf.record = self
                    lf.name = os.path.join(uncompress_file, filename)
                    lf.save()
                    lf.parse_log()
        
            for filename in filenames:
                suffix = filename.split('.')[-1]
                if suffix == 'json':
                    self.parse_json(os.path.join(uncompress_file, filename))
                elif suffix == 'metrics':
                    self.parse_metrics(os.path.join(uncompress_file, filename))
        self.save()


class LogFile(models.Model):
    record = models.ForeignKey(Record)
    name = models.CharField(max_length=255)
    file = models.FilePathField()
    host = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
    def parse_log(self):
        f = open(self.name)
        line = f.readline()
        output_flag = 0
        cmd = Cmd()
        while('' != line):
            if(output_flag):
                if(cmd.is_exit(line)):
                    output_flag = 0
                    cmd.exit = cmd.get_exitcode(line)
                    cmd.duration = cmd.get_duration(line)
                    cmd.logfile = self
                    cmd.output = cmd.output.strip()
                    cmd.save()
                else:
                    cmd.output += line
                    
            if(cmd.is_cmd(line)):
                cmd = Cmd()
                cmd.name = cmd.get_cmd(line)
                if(cmd.is_ssh()):
                    cmd.name = cmd.name.split('"')[1]
                cmd.time = cmd.get_time(line)
                
            if(cmd.is_output(line)):
                output_flag = 1
            line = f.readline()
        f.close()
        return
    
class Cmd(models.Model):
    logfile = models.ForeignKey(LogFile)
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
    
    def is_ssh(self):
        pattern = re.compile(r'/usr/bin/ssh')
        return pattern.match(self.name)
    
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