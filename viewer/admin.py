from django.contrib import admin

from .models import Cmd,Log

# Register your models here.
admin.site.register(Log)
admin.site.register(Cmd)