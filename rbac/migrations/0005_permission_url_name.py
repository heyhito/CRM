# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2020-06-20 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0004_permission_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='url_name',
            field=models.CharField(default='1', max_length=32),
        ),
    ]
