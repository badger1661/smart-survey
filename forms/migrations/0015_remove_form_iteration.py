# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-06 16:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0014_auto_20180206_1650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='form',
            name='iteration',
        ),
    ]
