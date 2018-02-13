# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-29 20:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20171229_2020'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.School')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='Admin', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
