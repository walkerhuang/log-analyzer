# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cmd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('time', models.TimeField()),
                ('output', models.CharField(max_length=200)),
                ('duration', models.DurationField()),
                ('exit', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('logfile', models.FileField(upload_to='')),
                ('version', models.CharField(max_length=10)),
                ('padv', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='cmd',
            name='log',
            field=models.ForeignKey(to='viewer.Log'),
        ),
    ]
