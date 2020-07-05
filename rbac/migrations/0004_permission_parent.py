# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2020-06-20 07:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0003_menu_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Permission'),
        ),
    ]