# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2020-06-27 23:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0007_auto_20200627_2330'),
        ('sales', '0002_auto_20200614_1202'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consultrecord',
            options={'verbose_name_plural': '跟进记录'},
        ),
        migrations.AlterModelOptions(
            name='courserecord',
            options={'verbose_name_plural': '课程记录表'},
        ),
        migrations.AlterModelOptions(
            name='enrollment',
            options={'verbose_name_plural': '报名表'},
        ),
        migrations.AlterModelOptions(
            name='studyrecord',
            options={'verbose_name_plural': '学习记录表'},
        ),
        migrations.AddField(
            model_name='userinfo',
            name='roles',
            field=models.ManyToManyField(to='rbac.Role'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Campuses', verbose_name='校区'),
        ),
    ]
