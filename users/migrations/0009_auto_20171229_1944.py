# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-29 19:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20171229_1905'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subjects',
            new_name='Subject',
        ),
    ]
